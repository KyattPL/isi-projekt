import React from 'react';
import { Box, Typography, Card, CardContent, CardActions, Button } from '@mui/material';

function MatchInfoCard({ index, match, gameName, tagLine }) {
    let playersObj = match['info']['participants'];

    let playerId = playersObj.findIndex((e) => e['riotIdGameName'] === gameName && e['riotIdTagline'] === tagLine);
    let mins = Math.floor(match['info']['gameDuration'] / 60);
    let secs = match['info']['gameDuration'] % 60;
    let win = playersObj[playerId]['win'];

    let backgroundColor = win ? 'rgba(0, 0, 255, 0.5)' : 'rgba(255, 0, 0, 0.5)';
    let role = playersObj[playerId]['teamPosition'];
    let formattedMins = mins.toString().padStart(2, '0');
    let formattedSecs = secs.toString().padStart(2, '0');

    return (
        <Card sx={{
            marginBottom: '20px',
            backgroundColor: backgroundColor,
            borderRadius: '10px',
            boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)',
        }} key={index}>
            <CardContent sx={{ padding: '20px' }}>
                <Box display={'flex'} justifyContent={'space-between'}>
                    <Box display={'flex'}>
                        <Box marginRight={20} width={140}>
                            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
                                Result: {win ? 'Win' : 'Lose'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Role: {role === 'UTILITY' ? 'SUPPORT' : role}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Game length: {formattedMins}:{formattedSecs}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
                                Champion: {playersObj[playerId]['championName']}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Kills: {playersObj[playerId]['kills']}, Deaths: {playersObj[playerId]['deaths']}, Assists: {playersObj[playerId]['assists']}
                            </Typography>
                        </Box>
                    </Box>
                    <Box>
                        <Typography variant="body2" color="text.secondary">
                            Champion Level: {playersObj[playerId]['champLevel']}, Gold Earned: {playersObj[playerId]['goldEarned']}
                        </Typography>
                    </Box>
                </Box>
            </CardContent>
            <CardActions>
                <Button sx={{ marginLeft: 'auto' }}>Analysis</Button>
            </CardActions>
        </Card>
    );
}

export default MatchInfoCard;