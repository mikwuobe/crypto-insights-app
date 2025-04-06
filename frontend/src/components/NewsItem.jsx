import React from 'react';
import PropTypes from 'prop-types';
import { ListGroup, Badge, Image } from 'react-bootstrap';

const getSentimentVariant = (sentiment) => { sentiment = sentiment?.toUpperCase(); if (sentiment === 'POSITIVE') return 'success'; if (sentiment === 'NEGATIVE') return 'danger'; if (sentiment === 'NEUTRAL') return 'secondary'; return 'warning'; };
const formatDateTime = (isoString) => { if (!isoString) return 'No date'; try { const options = { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }; return new Date(isoString).toLocaleString(undefined, options); } catch (error) { console.error("Error formatting date:", isoString, error); return isoString; } };

function NewsItem({ article }) {
  if (!article) { return null; }

  const { title, source, url, published_at, sentiment, image_url } = article;
  const sentimentVariant = getSentimentVariant(sentiment);
  const formattedDate = formatDateTime(published_at);

  return (
    <ListGroup.Item action className="d-flex justify-content-between align-items-start flex-column flex-md-row gap-3">

      { }
      {image_url && (
        <Image
          src={image_url}
          alt={`${title || 'article image'}`} 
          style={{ width: '80px', height: '80px', objectFit: 'cover' }} 
          rounded
          className="flex-shrink-0 me-md-3"
          onError={(e) => { e.target.style.display = 'none'; }}
        />
      )}

      { }
      <div className="flex-grow-1">
        <div className="fw-bold mb-1">
          { }
          <a href={url} target="_blank" rel="noopener noreferrer" className="text-decoration-none me-2stretched-link">
            {title || 'No Title'}
          </a>
          { }
          <Badge bg={sentimentVariant} pill className="px-2 py-1" style={{ fontSize: '0.7em', verticalAlign: 'middle' }}>
             {sentiment || 'Unknown'}
          </Badge>
        </div>
        { }
        <small className="text-muted d-block">{source || 'Unknown Source'}</small>
        <small className="text-muted d-block">{formattedDate}</small>
      </div>

    </ListGroup.Item>
  );
}

NewsItem.propTypes = {
  article: PropTypes.shape({
     title: PropTypes.string, source: PropTypes.string, url: PropTypes.string.isRequired, published_at: PropTypes.string, sentiment: PropTypes.string, image_url: PropTypes.string,
  }),
};

export default NewsItem;