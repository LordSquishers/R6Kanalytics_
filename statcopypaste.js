scrapedOpData = {};

function depositOpStat(opName, data) {
    scrapedOpData[opName] = data;
}

function parsePlaytime(playtimeString) {
    var halves = playtimeString.split(' : ')
    return parseInt(halves[0].substring(0)) * 60 + parseInt(halves[1].substring(0))
}

TARGET_QUEUE = 'ranked'.toUpperCase()
document.getElementsByClassName('g2w_groupSwitch__option').forEach((item) => {
    if (item.innerText == TARGET_QUEUE) item.click();
})
document.getElementsByClassName('g2w_tabs__item').forEach((item) => {
    if (item.innerText == 'OPERATOR') item.childNodes[0].click();
})

try {
    for (var i = 0; i < 10; i++) {
        document.getElementsByClassName('g2w_datatable-actions__viewmore')[0].click();
        console.log(i);
    }
} catch (e) {
    console.log('Opened all operators!')
}

var opTable = document.getElementsByClassName('g2w_datatable-table')[0].tBodies[0].childNodes;
var statHeaders = document.getElementsByClassName('g2w_datatable-table')[0].tHead.childNodes[0];
for (var opTableIndex = 0; opTableIndex < opTable.length; opTableIndex++) {
    var opEntry = opTable[opTableIndex].childNodes;
    var opName = opEntry[0].innerText;
    console.log('Processing op: ' + opName);

    var opStatJSON = {};
    var opPlaytime = opEntry[1].innerText;
    opStatJSON["TIMEPLAYED"] = parsePlaytime(opPlaytime);

    for (var i = 2; i < opEntry.length; i++) {
        var statName = statHeaders.childNodes[i].innerText;
        var opStatEntry = parseFloat(opEntry[i].innerText);
        opStatJSON[statName] = opStatEntry;
    }
    console.log('Finished ' + opName);

    depositOpStat(opName, opStatJSON);
}

console.log(JSON.stringify(scrapedOpData));
