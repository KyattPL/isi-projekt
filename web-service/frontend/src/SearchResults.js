import React, { useEffect, useState } from 'react';
import { Container, Typography, CircularProgress, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

import MatchInfoCard from './MatchInfoCard';

function SearchResults() {
    const { gameName, tagLine } = useParams();
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            const response = await fetch(`http://localhost:8000/matches_data_by_riot_id/${gameName}/${tagLine}`);
            const data = await response.json();
            setData(data);
            console.log(data);
            setLoading(false);
        };

        fetchData();
    }, [gameName, tagLine]);

    return (
        <Container>
            <Typography marginTop={2} variant="h4" component="h1" gutterBottom align='center'>
                {gameName}#{tagLine} match history:
            </Typography>
            {loading ? (
                <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
                    <CircularProgress />
                </Box>
            ) : (
                data.map((match, index) => <MatchInfoCard index={index} match={match} gameName={gameName} tagLine={tagLine} />)
            )}
        </Container>
    );
}

export default SearchResults;