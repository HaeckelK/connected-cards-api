# connected-cards-api PROTOTYPE

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![python](https://img.shields.io/badge/python-3.7-blue.svg)]()

[](./assets/banner.png)
<img
  src="https://github.com/HaeckelK/connected-cards-api/raw/main/assets/banner.png"
  alt="Connected Cards"
  width="750"
/>

Backend API for Connected Cards Flash Cards App.

## Motivations and Targets
I've started this project as I wanted some features in a Flashcard system that I can't easily get from Anki:
- Programmatic creation of cards without running desktop application.
- API centric backend.
- Create dependency graphs between notes which will prevent them being learnable until certain conditions have been met.
- Marking groups of notes as similar

  For example say you're learning French vocabulary and you've created several cards for colour words. To avoid confusing the new words with each other you might want to insist that you can't study more than n cards from that group in one day.
