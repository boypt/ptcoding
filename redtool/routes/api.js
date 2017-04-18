var debug = require('debug')('redtool:api');
var express = require('express');
var router = express.Router();
var http = require('http');

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
    } else {
      debug(`http status code ${statusCode}`);
      res.status(500).send('Server Error');
    }
  });
});

module.exports = router;
