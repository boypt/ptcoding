var debug = require('debug')('redtool:storage');
var Datastore = require('nedb')
  , db = new Datastore({ filename: 'storage.db', autoload: true });
// You can issue commands right away


exports.getall = function (callback) {
  db.find({}, callback);
}

exports.get = function (key, callback) {
  const query = {idnt:key};
  debug(query);
  db.findOne(query, callback);
}

exports.set = function (key, value, callback) {
  db.update({idnt:key}, value, {upsert:true}, callback);
  debug(value);
}
