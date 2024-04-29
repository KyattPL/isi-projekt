import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  CircularProgress,
  Box,
  Button,
} from "@mui/material";
import { useParams } from "react-router-dom";

import MatchInfoCard from "./MatchInfoCard";

function SearchResults() {
  const { gameName, tagLine } = useParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [lastMatchIndex, setLastMatchIndex] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/matches_data_by_riot_id/${gameName}/${tagLine}`
      );
      const data = await response.json();
      setData(data);
      setLastMatchIndex(9);
      setLoading(false);
    };

    fetchData();
  }, [gameName, tagLine]);

  const handleRefresh = async () => {
    setLoading(true);
    const response = await fetch(
      `http://localhost:8000/refresh_matches_data_by_riot_id/${gameName}/${tagLine}`
    );
    const data = await response.json();
    setData(data);
    setLastMatchIndex(9);
    setLoading(false);
  };

  const handleLoadMore = async () => {
    setLoadingMore(true);
    const response = await fetch(
      `http://localhost:8000/next10_matches_data_by_riot_id/${gameName}/${tagLine}/${
        lastMatchIndex + 1
      }`
    );
    const data = await response.json();
    setData((prev) => [...prev, ...data]);
    setLoadingMore(false);
  };

  return (
    <Container>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        marginBottom={2}
      >
        <Typography
          marginTop={2}
          variant="h4"
          component="h1"
          gutterBottom
          align="center"
        >
          {gameName}#{tagLine} match history:
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleRefresh}
          style={{ marginLeft: "auto" }}
        >
          Refresh
        </Button>
      </Box>
      {loading ? (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          height="100vh"
        >
          <CircularProgress />
        </Box>
      ) : (
        <>
          {data.map((match, index) => (
            <MatchInfoCard
              index={index}
              match={match}
              gameName={gameName}
              tagLine={tagLine}
            />
          ))}
          {loadingMore ? (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height="64px"
            >
              <CircularProgress />
            </Box>
          ) : (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              marginTop={2}
            >
              <Button
                variant="contained"
                color="primary"
                onClick={handleLoadMore}
              >
                Load 10 more
              </Button>
            </Box>
          )}
        </>
      )}
    </Container>
  );
}

export default SearchResults;
