import React from 'react';
import PropTypes from 'prop-types';
import { ListGroup, Alert } from 'react-bootstrap';
import NewsItem from './NewsItem';

function NewsList({ news, totalFilteredCount }) {
  
  if (news === null) {
    return <p>Loading news...</p>;
  }

  if (!Array.isArray(news) || totalFilteredCount === 0) {
    return (
      <Alert variant="info" className="mt-3">
        No news articles found matching the current filters.
      </Alert>
    );
  }

  return (
    <div className="mt-4">
      { }
      <h2 className="h5 mb-3">Recent News ({totalFilteredCount})</h2>
      <ListGroup variant="flush">
        { }
        {news.map((article) => (
          <NewsItem key={article.url || Math.random()} article={article} />
        ))}
      </ListGroup>
    </div>
  );
}

NewsList.propTypes = {
  news: PropTypes.arrayOf(PropTypes.object),
  totalFilteredCount: PropTypes.number 
};

NewsList.defaultProps = {
    totalFilteredCount: 0
};


export default NewsList;