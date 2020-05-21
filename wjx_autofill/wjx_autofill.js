/**
 * Env: Node.js
 */

// const puppeteer = require('puppeteer');
const puppeteer = require('puppeteer-core');
const CronJob = require('cron').CronJob;

const chrome_path = '/usr/bin/google-chrome'; // 根据自己的电脑修改


// 问卷ID
const ID = 69401977;
const SOURCE_URL = `https://www.wjx.cn/jq/${ID}.aspx`

// 问卷答案。单选题选项编号从1开始，多选题请使用编号数组'[编号1,编号2,...]'
const data = [
    'mozhewen',         // 1. 姓名
    6,                  // 2. 理论室
    2,                  // 3. 学生
    null,
    4,                  // 5. 目前位置：其他
    null,
    'XXXYYYZZZ',        // 7. 详细地址
    2,                  // 8. 否当天返京
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    1,                  // 17. 今日体温正常
    1,                  // 18. 本人家人身体状况正常
    null,
    null,
    2,                  // 21. 否去过湖北省
    2,                  // 22. 否有过接触
    2,                  // 23. 否14天内返京
    null,
    null,           
    3,                  // 26. 否隔离观察
    3,                  // 27. 否疑似/确诊
    '1234567890'        // 28. 联系方式
];


async function fillInForm() {
    const stamp = new Date();
    // 打开浏览器
    const browser = await puppeteer.launch({executablePath: chrome_path});
    // 新建标签页
    const page = await browser.newPage();
    // 访问问卷网址
    await page.goto(SOURCE_URL);
    // 填写问卷
    for (let i = 0; i < data.length; i++) {
        if (data[i] == null) continue; // 跳过不必答题
        switch(data[i].constructor) {
        case String: // 填空题
            await page.type('#q'+(i+1), data[i]); // 填写文字
            break;
        case Number: // 单选题
            await page.click(`a[rel="q${i+1}_${data[i]}"]`); // 点击选项
            break;
        case Array: // 多选题
            for (let j = 0; j < data[i].length; j++)
                await page.click(`a[rel="q${i+1}_${data[i][j]}"]`); // 点击选项
        // 目前只支持这些题目类型
        }
    }
    // 点击提交按钮
    await page.click('#submit_button');
    await browser.close();
    console.log(stamp.toDateString(), '[Done]');
}


// 每天11点，定时执行
new CronJob('0 0 11 * * *', fillInForm, null, true);
