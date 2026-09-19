import { ArrowUpRight, BedDouble, MapPin, Star, UsersRound } from "lucide-react";
import { Link } from "react-router-dom";

import type { Property } from "../types";


const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export function PropertyCard({ property }: { property: Property }) {
  return (
    <article className="property-card">
      <Link className="property-image-wrap" to={`/properties/${property.id}`}>
        <img
          className="property-image"
          src={property.coverImage || "/images/goa-villa.svg"}
          alt={property.title}
        />
        <span className="rating-pill">
          <Star size={14} fill="currentColor" /> {property.averageRating.toFixed(1)}
        </span>
      </Link>
      <div className="property-content">
        <div className="property-location">
          <MapPin size={15} /> {property.city}, {property.country}
        </div>
        <div className="property-title-row">
          <h3>{property.title}</h3>
          <Link aria-label={`View ${property.title}`} to={`/properties/${property.id}`}>
            <ArrowUpRight size={20} />
          </Link>
        </div>
        <p>{property.description}</p>
        <div className="property-meta">
          <span>
            <UsersRound size={16} /> {property.capacity} guests
          </span>
          <span>
            <BedDouble size={16} /> {property.bedrooms} bedrooms
          </span>
        </div>
        <div className="property-footer">
          <strong>{money.format(property.basePrice)}</strong>
          <span>per night</span>
        </div>
      </div>
    </article>
  );
}
