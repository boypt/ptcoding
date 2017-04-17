var express = require('express');
var router = express.Router();
var http = require('http');

router.get('/sina', function(req, res, next) {
  // res.send('respond with a resource');
  //$sinaurl = 'http://hq.sinajs.cn/ran='.$_GET['_'].'&list='.$_GET['list'];
  res.header('content-type', 'application/x-javascript; charset=GBK');
  // res.set('Content-Type', 'application/x-javascript; charset=GBK');
  const sinaurl = 'http://hq.sinajs.cn/ran=' + req.query._ + '&list=' + req.query.list;
  // console.log('sinaurl: '+sinaurl);

  http.get(sinaurl, (resource) => {
    const { statusCode } = resource;

    let error;
    if (statusCode === 200) {
      // console.log (resource);
      let rawData = Buffer.alloc(0);
      resource.on('data', (chunk) => {
        rawData = Buffer.concat([rawData, chunk]);
      });
      resource.on('end', () => {
          res.send(rawData);
      });
    } else {
      console.error(`Got error: ${e.message}`);
      res.send(`Got error: ${e.message}`);
    }
  });
});

module.exports = router;
