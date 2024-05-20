# R6 Kanalytics

This is a Python project that numerically analyzes operator data of two teams of five in Rainbow Six: Siege. Due to the lack of available APIs to retreive data, player data must be retrieved manually through the use of a JS script run in browser on the Ubisoft R6 Statistics webpage.

NOTE: Last used for Operation Heavy Mettle, but should work with new Operations unless the stats page has changed. You will need to add new operators to `lookup.py` to categorize them as ATK or DEF, otherwise they will default to one side.

# Usage:
To install, first run `pip install -r requirements.txt`.

To run:
`py kanalytics.py`. Output is in to console.

Create JSON files for each player using the provided `statcopypaste.js` script. Open the Ubisoft R6 Stats page, choose the player, and open the operators tab. Open the JS Developer Console on your browser of choice and paste the JS script contents. Copy the resulting data into the JSON file (name of the JSON file does not matter). You will need to modify the `kanalytics.py` file to point to the correct team folders. Team folders are placed in the same directory as the python file.

There is also "halo" folder, which converts Match Results pages from HaloWaypoint into a copy-pastable format for spreadsheets. Just a nice little utility.

# Details:

There are two metrics for operators: `Impact`, and `RoamEff`.

By default Kanalytics will present a ban report, featuring a Ban Priority for ATK and DEF, operator analysis of the opponents, and operator analysis of your own team. Verbose mode details the individual stats of each player, per team.

`Impact` is a combination of *Win %, Wins, K/D, Kills per Round, and Operator Presence*. Individual `Impact` scores tend to stay below 80 (with the exception of pros), while `Team Impact` scores tend to be larger, reaching values of 160 in the case of Spacestation Gaming.

`RoamEff` is a combination of operator effectiveness and the amount the player travels. More details as to how this metric may be intepreted can be found below.

# Interpretations:
- `Impact`
  - Positive values indicate team contribution.
  - Negative values indicate detriment to team.
  - Generally, any individual *Impact* greater than 25 means a player is proficient at the operator.
  - *Team Impact* is not easy to view objectively, and is better used in comparison with other *Team Impacts*.
- `RoamEff`
  - An operator that travels 400-500 meters per round (running the length of Kafe Dostoyevsky ~7 times) while doing nothing for the team can achieve a maximum *RoamEff* of 10. 
  - Large positive values (any greater than 15) indicate a player often obtains a high proportion of opening kills and positively influences the outcome of a round. These operators are the ones to keep an eye out for.
  - Negative values indicate a player is often the first death in a round with this operator. The more extreme the value, the more likely this is to happen.
  - Values between 0 and 10 generally indicate that this player stays close to objectives with this operator. Keep in mind that particularly successful players may exceed 10 *RoamEff* while travelling relatively little.
