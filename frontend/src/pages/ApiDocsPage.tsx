import { useEffect, useRef } from "react";
import SwaggerUI from "swagger-ui";
import "swagger-ui/dist/swagger-ui.css";

export default function ApiDocsPage() {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!container.current) return;
    SwaggerUI({
      domNode: container.current,
      url: "/api/openapi.yaml",
      deepLinking: true,
      displayRequestDuration: true,
      persistAuthorization: true,
      tryItOutEnabled: true,
    });
  }, []);

  return (
    <main className="api-docs-page">
      <div className="shell api-docs-heading">
        <p className="eyebrow">Engineering reference</p>
        <h1>Explore the StayEase API</h1>
        <p>
          Inspect schemas, authorize with a local JWT, and exercise the booking workflow
          against your running environment.
        </p>
      </div>
      <div className="api-docs-shell" ref={container} />
    </main>
  );
}
