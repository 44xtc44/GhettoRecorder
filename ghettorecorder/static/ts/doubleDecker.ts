// doubleDecker.js
"use strict";

/**
* Just for one SVG image. Reused in EisenRadio for Zeppelin.
* Python Zen (PEP20) say explicit is better than implicit. 
* TS does not care. let isTrue = true;  isTrue = 10; //$ error: Type '10' is not assignable to type 'boolean'
* I use multiple actions to do the same thing in this JS to TS migration, improve skills, document most differences. 
*/

declare var gPropNose: any;  // make the TS compiler happy; window... declare instance later
declare var gPropAxis: any;
declare var gScarfGroup: any;
declare var gPropReflect: any;
declare var doubleDecker: any;
/**
* Init doubleDecker. ``audioEnable()`` calls us on start.
*/
function enableAirplane() {
  // colorize plane
  let doubleDecker = new FourShadesSVG("#gAirOne"); 
  doubleDecker.pathListsGet();
  colorCreate( {colInstance: doubleDecker, arrLength:3, step:8} );
  doubleDecker.colorPalettePush();
  // colorize pilot
  let airOne_pilotTwo_neck = document.getElementById("airOne_pilotTwo_neck") as HTMLElement;
  airOne_pilotTwo_neck.style.fill = "#CC1100";
  let airOne_pilotTwo_scarfOne = document.getElementById("airOne_pilotTwo_scarfOne") as HTMLElement;
  airOne_pilotTwo_scarfOne.style.fill = "#CC1100";
  let airOne_pilotTwo_scarfTwo = document.getElementById("airOne_pilotTwo_scarfTwo") as HTMLElement;
  airOne_pilotTwo_scarfTwo.style.fill = "#CC1100";
  let airOne_pilotTwo_scarfThree = document.getElementById("airOne_pilotTwo_scarfThree") as HTMLElement;
  airOne_pilotTwo_scarfThree.style.fill = "#CC1100";
  let airOne_pilotTwo_scarfFour = document.getElementById("airOne_pilotTwo_scarfFour") as HTMLElement;
  airOne_pilotTwo_scarfFour.style.fill = "red";
  // show hide elements
  window.gPropNose = new ShowHideElemGroups("#gPropNose");
  window.gPropAxis = new ShowHideElemGroups("#gPropAxis" );
  window.gScarfGroup = new ShowHideElemGroups("#gScarfGroup");
  window.gPropReflect = new ShowHideElemGroups("#gPropReflect");
}
;
/**
* doubleDecker saves CPU, browser frame cycles during the show.
*/
function animatedAirplane() {
  if (hiddenOnOff.isSwitchedOn["svgAirOne"]) {  // called onClick on div element in index.html
    if (frameCount % 11 == 0) {  // mobile CPU need a rest, but anim will suffer
      gScarfGroup.update();  // created in enableAirplane()
      gPropReflect.update();
    }
    if (frameCount % 66 == 0) {
      gPropNose.update();
    }
    if (frameCount % 123 == 0) {
      gPropAxis.update();
    }
    // plane color
    if (frameCount % 543 == 0) {  // 60 frames per second; 10 sec calc new color plus shades
      window.doubleDecker = new FourShadesSVG("#gAirOne");  // feeder principle same as class ShowHideElemGroups 
      doubleDecker.pathListsGet();
      colorCreate( {colInstance: doubleDecker, arrLength:3, step:8} );
      doubleDecker.colorPalettePush();
    }
  }
}
;
/**
* Outsource the logic for color palette creation.
* could have used options style like in class HiddenOnOff.update (index.ts)
* (options: {colInstance: typeof doubleDecker, arrLength: number, step: number})
* options.colInstance
*/
type COL = { colInstance: typeof doubleDecker, arrLength: number, step: number };
function colorCreate({colInstance, arrLength, step}: COL) {
  let colorList = colInstance.colorPaletteMulti({arrLength:arrLength, step:step});  // four paths, next light value plus eight
  colInstance.hslInterpolationList = [
    colInstance.hslOne = colorList[0],  // hsl(339, 80%, 94%)
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
  constructor(
    public pathName: string,
    public pathsListArray = document.querySelectorAll(pathName + " path"),
    public pathIndex: number = 0,
    public pathList: string[] = []
    ) {
    this.pathListGet();
  }
  pathListGet() {
    // index is implicit of type number, recap
    for (let index = 0; index <= this.pathsListArray.length - 1; index++) {  // collection of paths to colorize; class FourShadesSVG
      let pID: string = this.pathsListArray[index].id;  // collection .id property
      this.pathList.push(pID);
    }
  }
  update() {
    for (let index = 0; index <= this.pathList.length - 1; index++) {
      let svgPath = document.getElementById(this.pathList[index]) as HTMLElement;

      if (index == this.pathIndex || (index - 1 < this.pathIndex && index > this.pathIndex + 1)) {
        svgPath.style.visibility = "hidden";
      } else {
        svgPath.style.visibility = "visible";
      }
    }
    this.pathIndex += 1;
    if (this.pathIndex > this.pathList.length - 1) {
      this.pathIndex = 0
    }
  }
}
/**
* doubleDecker SVG is constructed from four greyscale colored paths (names).
* It is the regex part of the name that counts here. "greyOne" and so forth.
* We use one nice base color and shade the grey colors in four steps by the hsl light value.
*/
class FourShadesSVG {
  constructor(
    public pathName: string,
    public pathsListArray = document.querySelectorAll(pathName + " path"),  // "#gAirOne path"
    public forbiddenColors = glob.numberRange(215, 275),  // no bad shadows; glob utility class at index.js
    public allColors = glob.numberRange(0, 360),  // hue circle, to list
    public niceColors: number[] = [],  // filtered colors, no forbidden
    public pathList: string[] = [],  // collector of all path name strings of the SVG group
    public greyOnePathList: string[] = [],  // filtered path names that match regex
    public greyTwoPathList: string[] = [],
    public greyThreePathList: string[] = [],
    public greyFourPathList: string[] = [],
    public greyLists: string[][] = [greyOnePathList, greyTwoPathList, greyThreePathList, greyFourPathList],  // could have used implicit, no string[][] type
    public hslOne: string = "",  // hsl(339, 80%, 94%)  JS color string 
    public hslTwo: string = "",  // hsl(339, 80%, 86%)
    public hslThree: string = "",  // hsl(339, 80%, 78%)
    public hslFour: string = "",  // hsl(339, 80%, 70%)
    public hslInterpolationList: string[] = [],  // hsl(339, 80%, 94%)  JS color strings
    ) {
    // init nice colors
    this.pickColors();
  }
  pickColors() {
    for (let idx = 0; idx <= this.allColors.length - 1; idx++) {
      if (!this.forbiddenColors.includes(idx)) this.niceColors.push(idx);
    }
  };
  pathListsGet() {
    /* SVG path names must match the grey keyword.
       I used to colorize the original image in grey colors.
       Gentler for the eyes in the long run. */
    for (let index = 0; index <= this.pathsListArray.length - 1; index++) {
      let pID = this.pathsListArray[index].id;
      this.pathList.push(pID);

      if (pID.includes("greyOne")) this.greyOnePathList.push(pID)
      if (pID.includes("greyTwo")) this.greyTwoPathList.push(pID)
      if (pID.includes("greyThree")) this.greyThreePathList.push(pID)
      if (pID.includes("greyFour")) this.greyFourPathList.push(pID)
    }
  }
  colorPaletteMulti(opt: {sat: number, light: number, step: number, arrLength: number}) {
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
    if(opt.sat === undefined) opt.sat = 80;
    const sat = opt.sat;
    if(opt.light === undefined) opt.light = 35;
    const light = opt.light;
    if(opt.step === undefined) opt.step = 4;
    const step = opt.step;
    let raise = 0;
    const arrLength = opt.arrLength;

    let retList = [];
    for(let idx = 0; idx <= arrLength; idx++) {
      retList.push("hsl(" + hueNum + "," + sat + "%," + (light + raise) + "%)");  // raise by step
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
        let svgPathElem = document.getElementById(greyShad[kIndex]) as HTMLElement;
        svgPathElem.style.fill = this.hslInterpolationList[index];
      }
    }
  }
}
;
