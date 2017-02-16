# Isolation Heuristics Analysis
by Terence So

## Summary

Three custom players were evaluated for this project: **Aggressive**, **Balanced**, and **Monte Carlo**, each representing the primary strategy of the custom player in game of Isolation. Each player was evaluated using the provided tournament format. A baseline strategy **ID_Improved** was used with a winrate of **62.19%**. The following are the results in summary:

* The Aggressive strategy performed near ID_Improved with a winrate of **60.94%**.
* The Balanced Strategy performed markedly better at a **67.81%** winrate.
* Finally, the Monte Carlo strategy had the best performance with a winrate of **71.88%**.

## Evaulation and Analysis

To increase the accuracy of final score, the tournament format was slightly modified by bumping up the number of matches played from 20 to 40.

### Aggressive

Formula: `blank spaces - opponent moves`

This strategy was designed as direct counter to the Open strategy. Whereas the Open player plays defensively by favoring board states with more open moves, the Aggressive strategy actively limits the opponent's moves without regard for its own safety.

The motivation for this strategy is that the horizon effect is particularly pronounced in this version of Isolation since valid moves are L-shaped 'knight' moves. Unlike regular isolation, each new position allows for a completely different set of possible next board positions. So while it may seem like a position with a lot of open moves may be a good idea, it may very well be a trap where all the next moves are the player's last.



### Balanced

### Monte Carlo

## Full Results

```
*************************
 Evaluating: ID_Improved
*************************

Playing Matches:
----------
  Match 1: ID_Improved vs   Random    	Result: 37 to 3
  Match 2: ID_Improved vs   MM_Null   	Result: 27 to 13
  Match 3: ID_Improved vs   MM_Open   	Result: 20 to 20
  Match 4: ID_Improved vs MM_Improved 	Result: 18 to 22
  Match 5: ID_Improved vs   AB_Null   	Result: 23 to 17
  Match 6: ID_Improved vs   AB_Open   	Result: 22 to 18
  Match 7: ID_Improved vs AB_Improved 	Result: 21 to 19


Results:
----------
ID_Improved         60.00%

*************************
Evaluating: Student Aggressive
*************************

Playing Matches:
----------
  Match 1: Student Aggressive vs   Random    	Result: 36 to 4
  Match 2: Student Aggressive vs   MM_Null   	Result: 28 to 12
  Match 3: Student Aggressive vs   MM_Open   	Result: 24 to 16
  Match 4: Student Aggressive vs MM_Improved 	Result: 16 to 24
  Match 5: Student Aggressive vs   AB_Null   	Result: 26 to 14
  Match 6: Student Aggressive vs   AB_Open   	Result: 26 to 14
  Match 7: Student Aggressive vs AB_Improved 	Result: 22 to 18


Results:
----------
Student Aggressive     63.57%

*************************
Evaluating: Student Balanced
*************************

Playing Matches:
----------
  Match 1: Student Balanced vs   Random    	Result: 34 to 6
  Match 2: Student Balanced vs   MM_Null   	Result: 29 to 11
  Match 3: Student Balanced vs   MM_Open   	Result: 17 to 23
  Match 4: Student Balanced vs MM_Improved 	Result: 20 to 20
  Match 5: Student Balanced vs   AB_Null   	Result: 28 to 12
  Match 6: Student Balanced vs   AB_Open   	Result: 24 to 16
  Match 7: Student Balanced vs AB_Improved 	Result: 25 to 15


Results:
----------
Student Balanced     63.21%

*************************
 Evaluating: Student MCS
*************************

Playing Matches:
----------
  Match 1: Student MCS vs   Random    	Result: 36 to 4
  Match 2: Student MCS vs   MM_Null   	Result: 34 to 6
  Match 3: Student MCS vs   MM_Open   	Result: 25 to 15
  Match 4: Student MCS vs MM_Improved 	Result: 27 to 13
  Match 5: Student MCS vs   AB_Null   	Result: 34 to 6
  Match 6: Student MCS vs   AB_Open   	Result: 27 to 13
  Match 7: Student MCS vs AB_Improved 	Result: 25 to 15


Results:
----------
Student MCS         74.29%
```
