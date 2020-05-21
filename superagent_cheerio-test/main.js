let superagent = require('superagent')
let cheerio = require('cheerio');
let fs = require('fs');

superagent.get('https://www.baidu.com')
    .set("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36")
    .end(function (err, res) {
        console.log(res.text);
        fs.writeFileSync("./temp.html", res.text);
    });

function post(html) {
    console.log(html);
    let $ = cheerio.load(html);
    fs.writeFileSync("./temp.html", html);
    //console.log($("p").html())
}
