# Sound-Amplifier
Computer vision app that controls speakers volume via hand command given from web cam.

Implemented command is done with thumb and index finger. If those fingers are completely separated speaker is set to 100% of its strength. If they are pressed together one on another speaker is set to 0% of its strength. 
Command can be shown with each hand, left and right, but it must be single hand shown in frame. Solution is implemented in a way that allows hand to be placed in any distance from a camera and in any angle, as long landmarks of a hand can be detected.

Technologies that were used:
- Python
- OpenCV
- Mediapipe
