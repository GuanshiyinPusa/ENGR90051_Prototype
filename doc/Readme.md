## Steps to set up this program
1. Install Python
- Windows: search python in Microsoft Store Most suggest way~
- Mac/Windows: install python on python website. follow the lead.

2. Install Streamlit
https://streamlit.io/#install
Install streamlit use the cmd in powershell/bash/mac's bash
```
pip install streamlit
```
use
```
streamlit hello
```
to see if that is working. 

3. How to run the code with streamlit
Inside the folder that u can download on onedrive, run: 
```
streamlit run filename.py
```

For example to run prop1.py:
```
streamlit run prop1.py
```

A webpage will pop up in your browser -- chrome or Safari.

4. Code Strucutre
- back.png is the back of the card
- Fronts/ folder contains all the card front u want.

- PS: If u put in 5 pngs, there will be 5 cards. It is not a constant size, u
can put how many png u want, the code will take in how many.

5. Code logic
Everytime a draw card is clicked. It is reshuffled first, then the system pick
random 3 from the card pool. PS: It doesn't have to be 3, we can change that.

6. Suggested Workflow
- The students have the system linked to their account. The TCS staff or whoever
will take control of this will have the admin roles. They are able to add points
to students' accounts.
- To play around with this system, students need to:
    - Bring e-waste to desired locations -- TCS, etc.
    - The staff will examine the amount and species of their e-waste.
    - The staff will transfer them into points and add that to student's
    account.
    - The student's point will eventually reach certain tiers and will allow
    them to draw cards from the webpage.
    - The studens can also see other people's points as a way of little
    competiton on recycling e-waste.
    - They draw cards -- funny or novel pics -- which keep them attracted.
    - Other than the fun of drawing cards, the cards can be used as coupon
    inside school canteen or ida bar, etc.

7. The idea behind
- Get the students motivated, the fun part is drawing cards and the card needs
to be hilarious. Coupon part is like cream on the top, as a motive bounded with
real object.


## TODOs

- Looking at other people's account

- Rework on the points progress bar. I see what i can do.

- Find funny pics? I reckon, EE guys asking others for opinions
the code resize the image, so sth like a phone vertical photo, or phone wallapper size

- Ask around for testing~

- Gonna use Ai in code and picture gen, should mention that.

- Points assignment:
- So far, the most basic idea is that:
    - Resistor is like 1 point.
    - PC is like 1000 points. 
    - PCB is like 10 to 100, varies depends on size. 

So the TCS staff/bin to evaluate based on the points system we designed. And we
gonna say like they can change it every year/sms to make sure the right points,
that said, 1000 may be not so incentive to students to bring them to TCS.

I am really happy with prop8 so far. You can experience the basic functions on
it.
In prop9 I added the congrat message on the left side panel. I think that is
enough as a demo.
