// doubleDecker.js
"use strict";
/**
* Init doubleDecker. ``audioEnable()`` calls us on start.
*/
function enableAirplane() {
    // colorize plane
    let doubleDecker = new FourShadesSVG("#gAirOne");
    doubleDecker.pathListsGet();
    colorCreate({ colInstance: doubleDecker, arrLength: 3, step: 8 });
    doubleDecker.colorPalettePush();
    // colorize pilot
    let airOne_pilotTwo_neck = document.getElementById("airOne_pilotTwo_neck");
    airOne_pilotTwo_neck.style.fill = "#CC1100";
    let airOne_pilotTwo_scarfOne = document.getElementById("airOne_pilotTwo_scarfOne");
    airOne_pilotTwo_scarfOne.style.fill = "#CC1100";
    let airOne_pilotTwo_scarfTwo = document.getElementById("airOne_pilotTwo_scarfTwo");
    airOne_pilotTwo_scarfTwo.style.fill = "#CC1100";
    let airOne_pilotTwo_scarfThree = document.getElementById("airOne_pilotTwo_scarfThree");
    airOne_pilotTwo_scarfThree.style.fill = "#CC1100";
    let airOne_pilotTwo_scarfFour = document.getElementById("airOne_pilotTwo_scarfFour");
    airOne_pilotTwo_scarfFour.style.fill = "red";
    // show hide elements
    window.gPropNose = new ShowHideElemGroups("#gPropNose");
    window.gPropAxis = new ShowHideElemGroups("#gPropAxis");
    window.gScarfGroup = new ShowHideElemGroups("#gScarfGroup");
    window.gPropReflect = new ShowHideElemGroups("#gPropReflect");
}
;
/**
* doubleDecker saves CPU, browser frame cycles during the show.
*/
function animatedAirplane() {
    if (hiddenOnOff.isSwitchedOn["svgAirOne"]) { // called onClick on div element in index.html
        if (frameCount % 11 == 0) { // mobile CPU need a rest, but anim will suffer
            gScarfGroup.update(); // created in enableAirplane()
            gPropReflect.update();
        }
        if (frameCount % 66 == 0) {
            gPropNose.update();
        }
        if (frameCount % 123 == 0) {
            gPropAxis.update();
        }
        // plane color
        if (frameCount % 543 == 0) { // 60 frames per second; 10 sec calc new color plus shades
            window.doubleDecker = new FourShadesSVG("#gAirOne"); // feeder principle same as class ShowHideElemGroups 
            doubleDecker.pathListsGet();
            colorCreate({ colInstance: doubleDecker, arrLength: 3, step: 8 });
            doubleDecker.colorPalettePush();
        }
    }
}
;
function colorCreate({ colInstance, arrLength, step }) {
    let colorList = colInstance.colorPaletteMulti({ arrLength: arrLength, step: step }); // four paths, next light value plus eight
    colInstance.hslInterpolationList = [
        colInstance.hslOne = colorList[0], // hsl(339, 80%, 94%)
        colInstance.hslTwo = colorList[1],
        colInstance.hslThree = colorList[2],
        colInstance.hslFour = colorList[3],
    ];
}
;
/**
* Show or hide multiple DOM element groups at once.
* Store current index of switched element in path list.
* <code>myGroup = new ShowHideElemGroups( {pathList: "#gScarfGroup"}) ; path string is attached in constructor</code>
*/
class ShowHideElemGroups {
    constructor(pathName, pathsListArray = document.querySelectorAll(pathName + " path"), pathIndex = 0, pathList = []) {
        this.pathName = pathName;
        this.pathsListArray = pathsListArray;
        this.pathIndex = pathIndex;
        this.pathList = pathList;
        this.pathListGet();
    }
    pathListGet() {
        // index is implicit of type number, recap
        for (let index = 0; index <= this.pathsListArray.length - 1; index++) { // collection of paths to colorize; class FourShadesSVG
            let pID = this.pathsListArray[index].id; // collection .id property
            this.pathList.push(pID);
        }
    }
    update() {
        for (let index = 0; index <= this.pathList.length - 1; index++) {
            let svgPath = document.getElementById(this.pathList[index]);
            if (index == this.pathIndex || (index - 1 < this.pathIndex && index > this.pathIndex + 1)) {
                svgPath.style.visibility = "hidden";
            }
            else {
                svgPath.style.visibility = "visible";
            }
        }
        this.pathIndex += 1;
        if (this.pathIndex > this.pathList.length - 1) {
            this.pathIndex = 0;
        }
    }
}
/**
* doubleDecker SVG is constructed from four greyscale colored paths (names).
* It is the regex part of the name that counts here. "greyOne" and so forth.
* We use one nice base color and shade the grey colors in four steps by the hsl light value.
*/
class FourShadesSVG {
    constructor(pathName, pathsListArray = document.querySelectorAll(pathName + " path"), // "#gAirOne path"
    forbiddenColors = glob.numberRange(215, 275), // no bad shadows; glob utility class at index.js
    allColors = glob.numberRange(0, 360), // hue circle, to list
    niceColors = [], // filtered colors, no forbidden
    pathList = [], // collector of all path name strings of the SVG group
    greyOnePathList = [], // filtered path names that match regex
    greyTwoPathList = [], greyThreePathList = [], greyFourPathList = [], greyLists = [greyOnePathList, greyTwoPathList, greyThreePathList, greyFourPathList], // could have used implicit, no string[][] type
    hslOne = "", // hsl(339, 80%, 94%)  JS color string 
    hslTwo = "", // hsl(339, 80%, 86%)
    hslThree = "", // hsl(339, 80%, 78%)
    hslFour = "", // hsl(339, 80%, 70%)
    hslInterpolationList = []) {
        this.pathName = pathName;
        this.pathsListArray = pathsListArray;
        this.forbiddenColors = forbiddenColors;
        this.allColors = allColors;
        this.niceColors = niceColors;
        this.pathList = pathList;
        this.greyOnePathList = greyOnePathList;
        this.greyTwoPathList = greyTwoPathList;
        this.greyThreePathList = greyThreePathList;
        this.greyFourPathList = greyFourPathList;
        this.greyLists = greyLists;
        this.hslOne = hslOne;
        this.hslTwo = hslTwo;
        this.hslThree = hslThree;
        this.hslFour = hslFour;
        this.hslInterpolationList = hslInterpolationList;
        // init nice colors
        this.pickColors();
    }
    pickColors() {
        for (let idx = 0; idx <= this.allColors.length - 1; idx++) {
            if (!this.forbiddenColors.includes(idx))
                this.niceColors.push(idx);
        }
    }
    ;
    pathListsGet() {
        /* SVG path names must match the grey keyword.
           I used to colorize the original image in grey colors.
           Gentler for the eyes in the long run. */
        for (let index = 0; index <= this.pathsListArray.length - 1; index++) {
            let pID = this.pathsListArray[index].id;
            this.pathList.push(pID);
            if (pID.includes("greyOne"))
                this.greyOnePathList.push(pID);
            if (pID.includes("greyTwo"))
                this.greyTwoPathList.push(pID);
            if (pID.includes("greyThree"))
                this.greyThreePathList.push(pID);
            if (pID.includes("greyFour"))
                this.greyFourPathList.push(pID);
        }
    }
    colorPaletteMulti(opt) {
        /**
         * Reusable, see EisenRadio Zeppelin.
         * Multiple, custom step values for SVG path animation, colorize a doppelDecker, zeppelin
         * colorPaletteGet() had an error. [35,39,47,59] is NOT step 4 :)
         * Return an array of step count length. .colorPaletteMulti({arrLength:7}); // for 8 paths
         *
         * One must take care that step is small enough to not get multiple val > 95%; pure white
         * let colorList = fourShades.colorPaletteMulti({arrLength:3, step:8});
        */
        let hueNum = glob.getRandomIntInclusive(0, this.niceColors.length - 1);
        if (opt.sat === undefined)
            opt.sat = 80;
        const sat = opt.sat;
        if (opt.light === undefined)
            opt.light = 35;
        const light = opt.light;
        if (opt.step === undefined)
            opt.step = 4;
        const step = opt.step;
        let raise = 0;
        const arrLength = opt.arrLength;
        let retList = [];
        for (let idx = 0; idx <= arrLength; idx++) {
            retList.push("hsl(" + hueNum + "," + sat + "%," + (light + raise) + "%)"); // raise by step
            raise += step;
        }
        return retList;
    }
    colorPalettePush() {
        /* Assign the color to the list of paths.
         */
        for (let index = 0; index <= this.greyLists.length - 1; index++) {
            let greyShad = this.greyLists[index];
            for (let kIndex = 0; kIndex <= greyShad.length - 1; kIndex++) {
                let svgPathElem = document.getElementById(greyShad[kIndex]);
                svgPathElem.style.fill = this.hslInterpolationList[index];
            }
        }
    }
}
;
