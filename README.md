# 🐍 Snake AI Game — BFS vs A*

An intelligent version of the classic Snake game implemented in Python using Pygame.  
This project compares two popular AI pathfinding algorithms — **Breadth-First Search (BFS)** and **A\*** — to evaluate their efficiency in real-time gameplay.

## 🎯 Project Objective
Transform the traditional Snake game into an educational AI platform to:
- Compare BFS and A* algorithms.
- Measure computational efficiency using **Nodes Expanded**.
- Analyze real-time performance in a dynamic grid environment.

## 🧠 Algorithms Used
### BFS (Breadth-First Search)
- Uninformed search algorithm.
- Guarantees the shortest path in unweighted grids.
- Expands many nodes → higher computational cost.

### A* (A-Star Search)
- Informed search algorithm using **Manhattan Distance heuristic**.
- Uses f(n) = g(n) + h(n).
- Expands significantly fewer nodes → higher efficiency.
- Finds the same optimal path as BFS with less computation.

## 🏗️ System Architecture
- Dual-board setup (20×20 grid each).
- Left board: BFS agent.
- Right board: A* agent.
- Both agents run simultaneously under identical conditions.
- Snake body is treated as obstacles.

## 🛠️ Technologies & Tools
- Python 3
- Pygame
- Data Structures:
  - deque (for BFS queue)
  - heapq (for A* priority queue)

## 📊 Performance Metrics
- Nodes Expanded (primary metric)
- Foods collected
- Alive time (in advanced version)
- Real-time comparison panel

## 🚀 How to Run
1. Install dependencies:
```bash
pip install pygame
```
-Run the main file:
```bash
python Snake\ Game.py
```
-Or for the advanced race version:
```bash
python Snake\ Game\ Alt.py
```

## 📁 Project Files
- Snake Game.py → Dual-board BFS vs A* race version.
- Snake Game Alt.py → Advanced race with timer, results & CSV export.
- Reports & Presentations → AI comparison analysis.

## 🔮 Future Work
- Implement Longest Safe Path strategy.
- Add Hamiltonian Cycle algorithm.
- Improve deadlock avoidance for long snake bodies.

## 🎮 User Play Version (Web Version)
- A web-based manual version of the Snake game.
- The player controls the snake using the keyboard.
- Used as a baseline for comparison with the AI-controlled version.

🌐 Play Online:  
https://nourravsnakegameweb.netlify.app/

---

## 📜 Copyright

This project is available for personal and educational use. If you intend to use it for commercial purposes, please contact me for permission.

---

## 📞 Contact

For questions or suggestions, please open an issue or contact:
Noura Maher Elamin
[LinkedIn](https://www.linkedin.com/in/nouramaher/)
[GitHub](https://github.com/NouraMaher)

---

<div align="center">

⭐️ **If you find this project helpful, please give it a star!**

</div>
