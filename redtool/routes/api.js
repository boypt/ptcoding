var debug = require('debug')('redtool:api');
var express = require('express');
var router = express.Router();
var http = require('http');
var path = require('path');
var fs = require('fs');

router.get('/sina', function(req, res, next) {

  if(!req.query.list) {
    res.status(400).send('Bad Request');
    return;
  }

  res.set('content-type', 'application/x-javascript; charset=GBK');
  const sinaurl = `http://hq.sinajs.cn/ran=${Math.random()}&list=${req.query.list}`;
  debug('sinaurl: '+sinaurl);

  http.get(sinaurl, (resource) => {
    const { statusCode } = resource;
    let error;
    if (statusCode === 200) {
      let rawData;
      resource.on('data', (chunk) => {
        if(Buffer.isBuffer(rawData)) {
          rawData = Buffer.concat([rawData, chunk]);
        } else {
          rawData = chunk;
        }
      });
      resource.on('end', () => {
        res.send(rawData);
      });
      resource.on('error', (e) => {
        debug(`problem with request: ${e.message}`);
        res.status(500).send(`problem with request: ${e.message}`);
      });
    } else {
      debug(`http status code ${statusCode}`);
      debug(resource);
      res.status(500).send('Server Error');
    }
  }).end();
});


router.post('/storage', function(req, res, next) {
  debug(`post idnt ${req.body.idnt}`);
  let filename = path.resolve(__dirname, '..', 'public', 'json', `${req.body.idnt}.json`)
  fs.writeFile(filename, JSON.stringify(req.body), (err) => {
    if (err) throw err;
    res.json({msg:'ok', idnt: req.body.idnt});
  });
});

router.get('/storage/all', function(req, res, next) {
  let jsondir = path.resolve(__dirname, '..', 'public', 'json');
  fs.readdir(jsondir, (err, files) => {
    let docs = []
    for(let fn of files) {
      if(fn.endsWith(".json")) {
         let obj = JSON.parse(fs.readFileSync(path.resolve(jsondir, fn)))
         docs.unshift(obj)
      }
    }
    res.json(docs);
  });
});


module.exports = router;
