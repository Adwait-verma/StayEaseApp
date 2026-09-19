from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier

import pymysql
from pymysql import Connection, MySQLError


def connection() -> Connection:
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root-test-password"),
        database=os.getenv("MYSQL_DATABASE", "stayease"),
        autocommit=True,
        charset="utf8mb4",
    )


def prepare_contenders(count: int) -> list[int]:
    with connection() as database, database.cursor() as cursor:
        cursor.execute("SELECT role_id FROM roles WHERE role_name = 'GUEST'")
        guest_role_id = cursor.fetchone()[0]
        cursor.executemany(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            [
                (
                    f"Race Guest {index:02d}",
                    f"race-{index:02d}@example.test",
                    "concurrency-test-not-a-login-credential",
                )
                for index in range(count)
            ],
        )
        cursor.execute(
            "SELECT user_id FROM users WHERE email LIKE 'race-%@example.test' "
            "ORDER BY user_id"
        )
        user_ids = [row[0] for row in cursor.fetchall()]
        cursor.executemany(
            "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            [(user_id, guest_role_id) for user_id in user_ids],
        )
    return user_ids


def attempt_booking(
    user_id: int,
    start_gate: Barrier,
    check_in,
    check_out,
) -> dict:
    with connection() as database, database.cursor() as cursor:
        start_gate.wait(timeout=20)
        try:
            cursor.execute("SET @created_booking_id = NULL")
            cursor.execute(
                "CALL sp_create_booking(%s, %s, %s, %s, %s, @created_booking_id)",
                (user_id, 2, check_in, check_out, 2),
            )
            while cursor.nextset():
                pass
            cursor.execute("SELECT @created_booking_id")
            return {
                "userId": user_id,
                "outcome": "created",
                "bookingId": cursor.fetchone()[0],
            }
        except MySQLError as error:
            return {
                "userId": user_id,
                "outcome": "rejected",
                "databaseCode": error.args[0],
                "reason": str(error.args[1]),
            }


def run_test(contenders: int) -> dict:
    user_ids = prepare_contenders(contenders)
    check_in = datetime.now(UTC).date() + timedelta(days=60)
    check_out = check_in + timedelta(days=3)
    start_gate = Barrier(contenders)

    with ThreadPoolExecutor(max_workers=contenders) as executor:
        results = list(
            executor.map(
                lambda user_id: attempt_booking(
                    user_id, start_gate, check_in, check_out
                ),
                user_ids,
            )
        )

    created = [result for result in results if result["outcome"] == "created"]
    rejected = [result for result in results if result["outcome"] == "rejected"]
    with connection() as database, database.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM bookings
            WHERE property_id = 2
              AND status IN ('PENDING', 'CONFIRMED')
              AND check_in < %s
              AND check_out > %s
            """,
            (check_out, check_in),
        )
        active_booking_count = cursor.fetchone()[0]

    result = {
        "contenders": contenders,
        "created": len(created),
        "rejected": len(rejected),
        "activeBookingsForDates": active_booking_count,
        "winningBookingId": created[0]["bookingId"] if created else None,
        "checkIn": check_in.isoformat(),
        "checkOut": check_out.isoformat(),
    }
    if len(created) != 1 or len(rejected) != contenders - 1:
        raise AssertionError(f"Expected one winner and {contenders - 1} rejections: {result}")
    if active_booking_count != 1:
        raise AssertionError(f"Expected one active booking in MySQL: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prove that concurrent StayEase bookings cannot overlap."
    )
    parser.add_argument("--contenders", type=int, default=25)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    if not 2 <= args.contenders <= 100:
        parser.error("--contenders must be between 2 and 100")

    result = run_test(args.contenders)
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("### Concurrent booking invariant")
    print()
    print(f"- Simultaneous contenders: **{result['contenders']}**")
    print(f"- Bookings created: **{result['created']}**")
    print(f"- Conflicting requests rejected: **{result['rejected']}**")
    print(f"- Active overlapping bookings in MySQL: **{result['activeBookingsForDates']}**")
    print(f"- Winning booking ID: **{result['winningBookingId']}**")


if __name__ == "__main__":
    main()
