// File: frontend/src/App.jsx
import { useState, useEffect, useCallback, useMemo } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col, Spinner, Alert, Form, Button } from 'react-bootstrap';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

import { fetchCryptoData } from './services/api';
import SentimentIndicator from './components/SentimentIndicator';
import NewsList from './components/NewsList';
import ThemeToggle from './components/ThemeToggle';

const REFRESH_INTERVAL_MS = 5 * 60 * 1000;
const ITEMS_PER_PAGE = 10;

function App() {
  console.log("App component rendering or re-rendering...");

  const [apiData, setApiData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSentiments, setSelectedSentiments] = useState(['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNKNOWN']);
  const [selectedSources, setSelectedSources] = useState([]);
  const [allSources, setAllSources] = useState([]);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(new Date());
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  useEffect(() => {
      if (apiData?.news) { const sources = [...new Set(apiData.news.map(a => a.source).filter(Boolean))].sort(); setAllSources(sources); if (selectedSources.length === 0 && sources.length > 0 && !isLoading) {setSelectedSources(sources);} } else if (!apiData) { setAllSources([]); setSelectedSources([]); }
  }, [apiData?.news, selectedSources.length, isLoading]);

  const handleSentimentChange = (e) => { const { value, checked } = e.target; setSelectedSentiments(prev => checked ? [...prev, value] : prev.filter(s => s !== value)); };
  const handleSourceChange = (e) => { const { value, checked } = e.target; setSelectedSources(prev => checked ? [...prev, value] : prev.filter(s => s !== value)); };

  const loadData = useCallback(async (isBackgroundRefresh = false) => {
    console.log("loadData function execution started.", { isBackgroundRefresh });
    if (!isBackgroundRefresh) setIsLoading(true);
    setIsRefreshing(true);
    if (!isBackgroundRefresh) setError(null);
    console.log(`Workspaceing data... (Background: ${isBackgroundRefresh}) Dates: ${startDate} to ${endDate}`);
    const data = await fetchCryptoData(startDate, endDate);
    console.log("fetchCryptoData completed. Result:", data ? "Got data" : "Failed or Null");
    if (data) { setApiData(data); setError(null); }
    else { if (!isBackgroundRefresh) { setError("Failed to fetch data from the server."); setApiData(null); } else { setError("Failed to refresh data. Displaying last known data."); } }
    setIsLoading(false);
    setIsRefreshing(false);
  }, [startDate, endDate]);

  useEffect(() => {
    console.log("Initial Load / Date Change useEffect running...");
    loadData(false);
    const intervalId = setInterval(() => { loadData(true); }, REFRESH_INTERVAL_MS);
    return () => { console.log("Clearing auto-refresh interval"); clearInterval(intervalId); };
  }, [loadData]);

  const filteredNews = useMemo(() => {
    if (!apiData?.news) return [];
    const lowerCaseSearchTerm = searchTerm.toLowerCase().trim();
    return apiData.news.filter(article => {
      const titleMatch = !lowerCaseSearchTerm || article.title?.toLowerCase().includes(lowerCaseSearchTerm);
      const sentimentMatch = selectedSentiments.includes(article.sentiment || 'UNKNOWN');
      const sourceMatch = selectedSources.includes(article.source || 'Unknown Source');
      return titleMatch && sentimentMatch && sourceMatch;
    });
  }, [apiData?.news, searchTerm, selectedSentiments, selectedSources]);

  const displayedNews = useMemo(() => {
    return filteredNews.slice(0, visibleCount);
  }, [filteredNews, visibleCount]);

  const handleLoadMore = () => {
    setVisibleCount(prevCount => prevCount + ITEMS_PER_PAGE);
  };

  useEffect(() => {
    setVisibleCount(ITEMS_PER_PAGE);
  }, [searchTerm, selectedSentiments, selectedSources, startDate, endDate]);

  return (
    <Container fluid className="mt-3 pb-5">
      <Row className="justify-content-md-center">
        <Col md={10} lg={8}>
          <Row className="mb-4 align-items-center">
             <Col> <h1 className="mb-0">AI Crypto Insights</h1> </Col>
             <Col xs="auto" className="d-flex align-items-center">
                 {isRefreshing && <Spinner animation="border" size="sm" className="me-2" title="Refreshing..." />}
                 <ThemeToggle />
             </Col>
          </Row>

          {isLoading && ( <div className="text-center"><Spinner animation="border" role="status" className="mt-5"><span className="visually-hidden">Loading...</span></Spinner><p>Loading initial data...</p></div> )}

          {!isLoading && error && ( <Alert variant="warning" className="mt-4"><Alert.Heading>Network Issue</Alert.Heading>{error}</Alert> )}

          {!isLoading && (
            <>
              {apiData && <SentimentIndicator overallSentiment={apiData.overall_sentiment} trend={apiData.trend} message={apiData.message} />}

               <Row className="my-4 align-items-center gx-3 p-3 border rounded bg-body-tertiary filter-section">
                  <Col xs={12} md={'auto'} className="mb-2 mb-md-0"><label htmlFor="startDate" className="fw-bold form-label">Date Range:</label></Col>
                  <Col xs={6} sm={4} md={3}> <DatePicker selected={startDate} onChange={(date) => setStartDate(date)} selectsStart startDate={startDate} endDate={endDate} isClearable placeholderText="Start Date" className="form-control form-control-sm" id="startDate" wrapperClassName="w-100"/> </Col>
                  <Col xs={6} sm={4} md={3}> <DatePicker selected={endDate} onChange={(date) => setEndDate(date)} selectsEnd startDate={startDate} endDate={endDate} minDate={startDate} isClearable placeholderText="End Date" className="form-control form-control-sm" id="endDate" wrapperClassName="w-100"/> </Col>
               </Row>

              {apiData && allSources.length > 0 && (
                <Row className="my-4 gx-3 p-3 border rounded bg-body-tertiary filter-section">
                    <Col md={6} className="mb-3 mb-md-0">
                       <fieldset>
                          <legend className="h6">Filter by Sentiment:</legend>
                          {['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNKNOWN'].map(sentiment => (
                          <Form.Check key={sentiment} inline type="checkbox" id={`sentiment-${sentiment}`} label={sentiment} value={sentiment} checked={selectedSentiments.includes(sentiment)} onChange={handleSentimentChange} />
                          ))}
                       </fieldset>
                    </Col>
                    <Col md={6}>
                       <fieldset>
                          <legend className="h6">Filter by Source:</legend>
                          <div style={{ maxHeight: '100px', overflowY: 'auto', border: '1px solid var(--border-color)', padding: '0.5rem' }}>
                              {allSources.map(source => (
                                  <Form.Check key={source} type="checkbox" id={`source-${source}`} label={source} value={source} checked={selectedSources.includes(source)} onChange={handleSourceChange} />
                              ))}
                          </div>
                       </fieldset>
                    </Col>
                </Row>
              )}

              <Form className="mb-3">
                 <Form.Group controlId="searchNewsInput">
                    <Form.Label className="visually-hidden">Search News Titles</Form.Label>
                    <Form.Control type="search" placeholder="Search news titles..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                 </Form.Group>
              </Form>

              <div aria-live="polite" aria-atomic="true">
                   {apiData && <NewsList news={displayedNews} totalFilteredCount={filteredNews.length} />}
              </div>

              {filteredNews.length > visibleCount && (
                <div className="text-center mt-4"><Button variant="outline-primary" onClick={handleLoadMore}>Load More ({visibleCount} / {filteredNews.length})</Button></div>
              )}

              {!apiData && !error && (<Alert variant="info" className="mt-4">Could not load initial data.</Alert>)}
            </>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default App;