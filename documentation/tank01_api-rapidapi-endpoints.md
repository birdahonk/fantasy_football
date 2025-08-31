# Tank01 API Endpoints (via RapidAPI)


## "Get Player List" endpoint
- This is the "Get Player List" endpoint. We'll need to start with this to match our player names to the player names in the Tank01 player list to link the "playerID" so we can use that to get other information from other endpoints.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_bb8c959a-d0b6-401b-a11d-519c0808a92f 

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLPlayerList", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get Fantasy Points Projections" endpoint
- This is the "Get Fantasy Points Projections" endpoint. We'll need this (along with the playerID) to get the projected points for each player for the pre-game tracking.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_244b2b2c-ab39-4f48-91f0-a6f01546dc06 

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLProjections?week=5&archiveSeason=2025&twoPointConversions=2&passYards=.04&passAttempts=-.5&passTD=4&passCompletions=1&passInterceptions=-2&pointsPerReception=1&carries=.2&rushYards=.1&rushTD=6&fumbles=-2&receivingYards=.1&receivingTD=6&targets=.1&fgMade=3&fgMissed=-1&xpMade=1&xpMissed=-1", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get NFL Team Roster" endpoint
- This is the Get NFL Team Roster endpoint. It appears that it might have some player stats as a parameter, but I'm not sure if this is the same as some of the other stats from the other endpoints. We'll need to look into this.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_7f8514bc-916d-43c6-8e10-5dc5915b82bd 

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLTeamRoster?teamID=6&teamAbv=CHI&getStats=true&fantasyPoints=true", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get NFL Depth Charts" endpoint
- This is the Get NFL Depth Charts endpoint. This should provide some useful data (I think it's the NFL team roster hierarchy for their players), which could help us understand if a particular player is going to get game time.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_abb2b764-220f-40de-9625-0fa7fbb1ca88

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLDepthCharts", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Top News and Headlines" endpoint
- This is the Top News and Headlines endpoint. We'll need this for news updates about players. We may need to follow links to get additioanl content beyond just the headlines.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_e2be6760-7da0-4244-8250-28e73c139034

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLNews?fantasyNews=true&maxItems=20", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get Daily Scoreboard - Live - Real Time" endpoint
- This is the Get Daily Scoreboard - Live - Real Time endpoint. It includes NFL game metadata and game stats. It might be useful, but we'll need to anayze and see.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_170ffbd1-36a2-4570-9671-0888277ee728

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLScoresOnly?gameDate=20250907&topPerformers=true", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get Player Information" endpoint
- This is the Get Player Information endpoint. It includes player stats that we might need.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_f9337033-5c90-47be-b369-17bc1c4b5f34

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLPlayerInfo?playerName=keenan_a&getStats=true", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get NFL Games and Stats For a Single Player" endpoint
- This is the Get NFL Games and Stats For a Single Player endpoint. It has player stats and Fantasy stats that we'll need.
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_aa6f788f-d365-4f02-b01a-d03c97dfe4c4

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLGamesForPlayer?playerID=3121422&fantasyPoints=true&twoPointConversions=2&passYards=.04&passTD=4&passInterceptions=-2&pointsPerReception=1&carries=.2&rushYards=.1&rushTD=6&fumbles=-2&receivingYards=.1&receivingTD=6&targets=0&defTD=6&xpMade=1&xpMissed=-1&fgMade=3&fgMissed=-3&idpTotalTackles=1&idpSoloTackles=1&idpTFL=1&idpQbHits=1&idpInt=1&idpSacks=1&idpPassDeflections=1&idpFumblesRecovered=1", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>

## "Get Changelog" endpoint
- The is the Get Changelog endpoint. It might be helpful to understand how the API or data updates change over time to highlight if we need to make adjustments to the scripts.
- https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_dcf1983c-3c29-4434-b4e5-ce0296683956

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLChangelog?maxDays=30", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>


## "Get NFL Teams" endpoint
- Data about the teams
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_43a5d210-b26c-4462-99ed-26ee79bca0e3

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLTeams?sortBy=standings&rosters=false&schedules=false&topPerformers=true&teamStats=true&teamStatsSeason=2024", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>


## "Get General Game Information" endpoint
- General game info
- @https://rapidapi.com/tank01/api/tank01-nfl-live-in-game-real-time-statistics-nfl/playground/apiendpoint_e5b27ceb-bb95-4409-b088-354f124b21f0

<Code Snippet>
``` python
import http.client

conn = http.client.HTTPSConnection("tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "9e399008f0msh5be410a22c3e054p11ff9bjsnc7ed29024909",
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
}

conn.request("GET", "/getNFLGameInfo?gameID=20260104_DET%40CHI", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```
</Code Snippet>
