// init dict
gameData = {};

// config
ACCEPTED_PARAMETERS = ["Shots Fired", "Shots Hit", "Damage Dealt", "Damage Taken", "Flag Captures", "Flag Capture Assists", "Total Zone Occupation Time", "Skull Scoring Ticks", "Conversions", "Extractions"];

function jsonFormatStat(statName) {
  var words = statName.toLowerCase().split(" ");
  var output = "";
  for(let word of words) {
    if(output != "") output += "_";
    output += word;
  }
  return output;
}

// get team name and overall score.
var teamElements = document.getElementsByClassName("pgcr-match-details_teamName__J8Cs2");

for(let teamElement of teamElements) {
  var teamName = teamElement.innerHTML;
  var teamScore = teamElement.parentElement.children[0].innerHTML;

  var keyEntry = teamName.toLowerCase() + "_score"
  gameData[keyEntry] = teamScore;
}

// get map, gamemode, and date/time of match.
var matchTimeElement = document.getElementsByClassName("pgcr-overview-heading_matchDate__y5u44")[0];
var matchTimeStrings = matchTimeElement.innerHTML.split(", ");

gameData["match_date"] = matchTimeStrings[0];
gameData["match_time"] = matchTimeStrings[1];

var matchDetailElements = document.getElementsByClassName("pgcr-match-details_detailValue___t_hI");
var gameMode = matchDetailElements[1].innerHTML;
var map = matchDetailElements[2].innerHTML;

gameData["gamemode"] = gameMode.split(":")[1];
gameData["map"] = map.toUpperCase();

var isVictory = document.getElementsByClassName("pgcr-match-details_result__dK78P")[0].innerHTML == "Victory";
var originTeam = document.getElementsByClassName("pgcr-match-details_result__dK78P")[0].nextElementSibling.innerHTML;

if((originTeam == "Eagle" && isVictory) || (originTeam == "Cobra" && !isVictory)) {
  gameData['eagle_win'] = true;
  gameData['cobra_win'] = false;
} else if((originTeam == "Eagle" && !isVictory) || (originTeam == "Cobra" && isVictory)) {
  gameData['cobra_win'] = true;
  gameData['eagle_win'] = false;
}

// expand all table elements
document.getElementsByClassName("team-stats-container_expanderButton__BduvC")[0].click();
gameData['players'] = {};

// loop through all players
for(let gamertagElement of document.getElementsByClassName("players-table_gamerTag__vcO0k")) {
  var gamertag = gamertagElement.innerHTML;
  var overallStatElement = gamertagElement.parentElement;
  var detailedStatElement = gamertagElement.parentElement.nextElementSibling;

  gameData['players'][gamertag] = {};

  var emblemLink = overallStatElement.childNodes[1].childNodes[0].src.split("blob:")[1]
  var playerScore = overallStatElement.childNodes[4].innerHTML;
  var kills = overallStatElement.childNodes[6].innerHTML;
  var deaths = overallStatElement.childNodes[7].innerHTML;
  var assists = overallStatElement.childNodes[8].innerHTML;

  gameData['players'][gamertag]["emblem"] = emblemLink;
  gameData['players'][gamertag]["score"] = playerScore;
  gameData['players'][gamertag]["kills"] = kills;
  gameData['players'][gamertag]["deaths"] = deaths;
  gameData['players'][gamertag]["assists"] = assists;

  for(let detailedElement of detailedStatElement.childNodes[1].getElementsByClassName("stat-table_key__eLJyM")) {
    var detailedStatName = detailedElement.innerHTML;
    var detailedElementStat = detailedElement.nextElementSibling.innerHTML;

    if(ACCEPTED_PARAMETERS.includes(detailedStatName)) {
      var keyEntry = jsonFormatStat(detailedStatName);
      gameData['players'][gamertag][keyEntry] = detailedElementStat;
    }
  }
}

// output to JSON.
console.log(JSON.stringify(gameData));
