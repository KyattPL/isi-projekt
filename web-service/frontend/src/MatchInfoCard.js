import React, { useState } from "react";
import {
    Box,
    Typography,
    Card,
    CardContent,
    CardActions,
    Button,
} from "@mui/material";

function MatchInfoCard({ index, match, gameName, tagLine, isLoggedIn, hasPremium }) {
    const [averages, setAverages] = useState({});
    const [wasAnalysisClicked, setWasAnalysisClicked] = useState(false);

    const doMatchAnalysis = async (playerChamp, playerStats, matchTime) => {
        try {
            const response = await fetch(`http://localhost:8000/get_snapshot_for_champ/${playerChamp}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            console.log(data);
            setAverages({
                kills: data[1] * matchTime,
                deaths: data[2] * matchTime,
                assists: data[3] * matchTime,
                lvl: data[4] * matchTime,
                gold: data[5] * matchTime,
                dmgDealt: data[6] * matchTime,
                dmgTaken: data[7] * matchTime,
                csAvg: data[9] * matchTime,
                visionAvg: data[10] * matchTime
            });
            setWasAnalysisClicked(true);
        } catch (error) {
            console.error("Failed to fetch match analysis:", error);
        }
    };

    const getAnalysisFormattedNum = (statValue, statAverage, isAboveGood = true) => {
        if (statValue > statAverage && isAboveGood) return <span style={{ color: "green", marginRight: "16px" }}>+{(statValue - statAverage).toFixed(2)}</span>;
        if (statValue < statAverage && !isAboveGood) return <span style={{ color: "green", marginRight: "16px" }}>+{(statAverage - statValue).toFixed(2)}</span>;
        if (statValue > statAverage && !isAboveGood) return <span style={{ color: "red", marginRight: "16px" }}>{(statAverage - statValue).toFixed(2)}</span>;
        if (statValue < statAverage && isAboveGood) return <span style={{ color: "red", marginRight: "16px" }}>{(statValue - statAverage).toFixed(2)}</span>;
        return <span style={{ color: "gray" }}>{statValue}</span>;;
    };

    let playersObj = match["info"]["participants"];

    let playerId = playersObj.findIndex(
        (e) => e["riotIdGameName"] === gameName && e["riotIdTagline"] === tagLine
    );

    let matchTime = match["info"]["gameDuration"];
    let mins = Math.floor(matchTime / 60);
    let secs = matchTime % 60;
    let win = playersObj[playerId]["win"];

    let backgroundColor = win ? "rgba(0, 0, 255, 0.5)" : "rgba(255, 0, 0, 0.5)";
    let role = playersObj[playerId]["teamPosition"];
    let formattedMins = mins.toString().padStart(2, "0");
    let formattedSecs = secs.toString().padStart(2, "0");

    let playerChamp = playersObj[playerId]["championName"];
    let playerStats = playersObj[playerId];

    console.log(playerStats);

    return (
        <Card
            sx={{
                marginBottom: "20px",
                backgroundColor: backgroundColor,
                borderRadius: "10px",
                boxShadow: "0 4px 8px 0 rgba(0,0,0,0.2)",
            }}
            key={index}
        >
            <CardContent sx={{ padding: "20px" }}>
                <Box display={"flex"} justifyContent={"space-between"}>
                    <Box display={"flex"}>
                        <Box marginRight={20} width={140}>
                            <Typography
                                variant="h5"
                                component="div"
                                sx={{ fontWeight: "bold" }}
                            >
                                Result: {win ? "Win" : "Lose"}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Role: {role === "UTILITY" ? "SUPPORT" : role}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Game length: {formattedMins}:{formattedSecs}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography
                                variant="h5"
                                component="div"
                                sx={{ fontWeight: "bold" }}
                            >
                                Champion: {playerChamp}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Kills: {playerStats["kills"]},
                                Deaths: {playerStats["deaths"]},
                                Assists: {playerStats["assists"]}
                            </Typography>
                            {wasAnalysisClicked && (
                                <Typography variant="body2">
                                    {getAnalysisFormattedNum(playerStats['kills'], averages['kills'])}
                                    {getAnalysisFormattedNum(playerStats['deaths'], averages['deaths'], false)}
                                    {getAnalysisFormattedNum(playerStats['assists'], averages['assists'])}
                                </Typography>
                            )}
                        </Box>
                    </Box>
                    <Box>
                        <Typography variant="body2" color="text.secondary">
                            Champion Exp: {playerStats["champExperience"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['champExperience'], averages['lvl'])}
                            </Typography>
                        )}
                        <br />
                        <Typography variant="body2" color="text.secondary">
                            Gold Earned: {playerStats["goldEarned"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['goldEarned'], averages['gold'])}
                            </Typography>
                        )}
                    </Box>
                    <Box>
                        <Typography variant="body2" color="text.secondary">
                            Dmg done: {playerStats["totalDamageDealtToChampions"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['totalDamageDealtToChampions'], averages['dmgDealt'])}
                            </Typography>
                        )}
                        <br />
                        <Typography variant="body2" color="text.secondary">
                            Dmg taken: {playerStats["totalDamageTaken"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['totalDamageTaken'], averages['dmgTaken'])}
                            </Typography>
                        )}
                    </Box>
                    <Box>
                        <Typography variant="body2" color="text.secondary">
                            CS: {playerStats["totalMinionsKilled"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['totalMinionsKilled'], averages['csAvg'])}
                            </Typography>
                        )}
                        <br />
                        <Typography variant="body2" color="text.secondary">
                            Vision score: {playerStats["visionScore"]}
                        </Typography>
                        {wasAnalysisClicked && (
                            <Typography variant="body2">
                                {getAnalysisFormattedNum(playerStats['visionScore'], averages['visionAvg'])}
                            </Typography>
                        )}
                    </Box>
                </Box>
            </CardContent>
            <CardActions>
                {isLoggedIn && (
                    <Button
                        sx={{ marginLeft: "auto", backgroundColor: hasPremium ? "gold" : "gray", color: hasPremium ? "white" : "black" }}
                        disabled={!hasPremium} onClick={() => doMatchAnalysis(playerChamp, playerStats, matchTime)}
                    >
                        Analysis
                    </Button>
                )}
            </CardActions>
        </Card>
    );
}

export default MatchInfoCard;
