// doubleDecker.js
"use strict";

/**
* Init doubleDecker. ``audioEnable()`` calls us on start.
*/
function enableAirplane() {
  // colorize plane
  let doubleDecker = new FourShadesSVG({ svgGroup: "#gAirOne" });
  doubleDecker.pathListsGet();
  colorCreate( {colInstance: doubleDecker, arrLength:3, step:8} );
  doubleDecker.colorPalettePush();
  // colorize pilot just for fun, red baron?
  document.getElementById("airOne_pilotTwo_neck").style.fill = "#CC1100";
  document.getElementById("airOne_pilotTwo_scarfOne").style.fill = "#CC1100";
  document.getElementById("airOne_pilotTwo_scarfTwo").style.fill = "#CC1100";
  document.getElementById("airOne_pilotTwo_scarfThree").style.fill = "#CC1100";
  document.getElementById("airOne_pilotTwo_scarfFour").style.fill = "red";
  // show hide elements
  window.gPropNose = new ShowHideElemGroups({ pathList: "#gPropNose" });
  window.gPropAxis = new ShowHideElemGroups({ pathList: "#gPropAxis" });
  window.gScarfGroup = new ShowHideElemGroups({ pathList: "#gScarfGroup" });
  window.gPropReflect = new ShowHideElemGroups({ pathList: "#gPropReflect" });
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
      window.doubleDecker = new FourShadesSVG({ svgGroup: "#gAirOne" });
      doubleDecker.pathListsGet();
      colorCreate( {colInstance: doubleDecker, arrLength:3, step:8} );
      doubleDecker.colorPalettePush();
    }
  }
}
;
function colorCreate(opt) {
  let colorList = opt.colInstance.colorPaletteMulti({arrLength:opt.arrLength, step:opt.step});  // four paths, next light value plus eight
  opt.colInstance.hslInterpolationList = [
    opt.colInstance.hslOne = colorList[0],  // hsl(339, 80%, 94%)
    opt.colInstance.hslTwo = colorList[1],
    opt.colInstance.hslThree = colorList[2],
    opt.colInstance.hslFour = colorList[3],
  ];
}
;
/**
* Show or hide multiple DOM element groups at once.
* Store current index of switched element in path list.
* <code>myGroup = new ShowHideElemGroups( {pathList: "#gScarfGroup"}) ; path string is attached in constructor</code>
*/
class ShowHideElemGroups {
  constructor(opt) {
    this.pathsListArray = document.querySelectorAll(opt.pathList + " path");  // a collection object
    this.pathIndex = 0;
    this.pathList = [];  // clean list
    this.pathListGet();
  }
  pathListGet() {
    for (let index = 0; index <= this.pathsListArray.length - 1; index++) {  // pathsListArray (s) class FourShadesSVG
      let pID = this.pathsListArray[index].id;  // collection .id
      this.pathList.push(pID);
    }
  }
  update() {
    for (let index = 0; index <= this.pathList.length - 1; index++) {
      let svgPath = document.getElementById(this.pathList[index]);

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
/* doubleDecker SVG is constructed with four greyscale colored paths (names).
* It is the name that counts here.
* We use one nice base color and shade the grey colors in four steps by hsl light value.
* <code>
* <path id="airOne_greyTwo_wing_tail"  , search "greyTwo"
* console.log(document.querySelectorAll("#gSvgSpeakerFlatWaves path")[0].id);
*
* glob.propReflect = new FourShadesSVG( {svgGroup:"#gPropReflect"} );
* glob.propReflect.pathListsGet();
* </code>
*/
class FourShadesSVG {
  constructor(options) {
    this.forbiddenColors = glob.numberRange(215, 275);  // bad shadows; glob utility class at index.js
    this.allColors = glob.numberRange(0, 360);  // hue circle, to list
    this.niceColors = [];
    this.pathsListArray = document.querySelectorAll(options.svgGroup + " path");  // options done "#gAirOne path"
    this.pathList = [];
    this.greyOnePathList = [];
    this.greyTwoPathList = [];
    this.greyThreePathList = [];
    this.greyFourPathList = [];
    this.greyLists = [this.greyOnePathList, this.greyTwoPathList, this.greyThreePathList, this.greyFourPathList];
    this.hslOne = "";
    this.hslTwo = "";
    this.hslThree = "";
    this.hslFour = "";
    this.hslInterpolationList = [];
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
  colorPaletteMulti(opt) {
    /* Reusable. Multiple, custom step values for SVG path animation, colorize a zeppelin, doppelDecker
       colorPaletteGet() had an error. [35,39,47,59] is NOT step 4 :)
       Return an array of step count length. .colorPaletteMulti({arrLength:7}); // for 8 paths

       One must take care that step is small enough to not get multiple val > 95%; pure white
       let colorList = fourShades.colorPaletteMulti({arrLength:3, step:8});
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
        let svgPathElem = document.getElementById(greyShad[kIndex]);
        svgPathElem.style.fill = this.hslInterpolationList[index];
      }
    }
  }
}
;
