import React from 'react';
import PropTypes from 'prop-types'; 
import { Card, Badge } from 'react-bootstrap';

const getSentimentVariant = (sentiment) => {
  sentiment = sentiment?.toUpperCase();
  if (sentiment === 'POSITIVE' || sentiment === 'BULLISH') {
    return 'success'; 
  } else if (sentiment === 'NEGATIVE' || sentiment === 'BEARISH') {
    return 'danger';
  } else {
    return 'secondary'; 
  }
};

function SentimentIndicator({ overallSentiment, trend, message }) {
  const sentimentVariant = getSentimentVariant(overallSentiment);
  const trendVariant = getSentimentVariant(trend);

  return (
    <Card className="mb-4 shadow-sm">
      <Card.Body>
        <Card.Title className="h5 mb-3">Overall Market Sentiment</Card.Title>
        <div className="d-flex justify-content-around align-items-center">
          <div className="text-center">
            <h6 className="text-muted mb-1">Overall</h6>
            <Badge pill bg={sentimentVariant} className="px-3 py-2 fs-6">
              {overallSentiment || 'Unknown'}
            </Badge>
          </div>
          <div className="text-center">
            <h6 className="text-muted mb-1">Trend</h6>
            <Badge pill bg={trendVariant} className="px-3 py-2 fs-6">
              {trend || 'Unknown'}
            </Badge>
          </div>
        </div>
        {message && <p className="small text-muted mt-3 mb-0">{message}</p>}
      </Card.Body>
    </Card>
  );
}

SentimentIndicator.propTypes = {
  overallSentiment: PropTypes.string,
  trend: PropTypes.string,
  message: PropTypes.string,
};

export default SentimentIndicator;