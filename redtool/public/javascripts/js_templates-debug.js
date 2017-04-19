(function() {
window["JST"] = window["JST"] || {};

window["JST"]["tpl_fundchart"] = function(obj) {
obj || (obj = {});
var __t, __p = '', __e = _.escape, __j = Array.prototype.join;
function print() { __p += __j.call(arguments, '') }
with (obj) {

 var r=Math.random(); ;
__p += '\n<div class="modal-header">\n  <h4 class="modal-title"><a href="http://fund.eastmoney.com/' +
__e( code ) +
'.html" target="_blank">' +
__e( name ) +
'</a></h4>\n  <button type="button" class="close" data-dismiss="modal" aria-label="Close">\n    <span aria-hidden="true">&times;</span>\n  </button>\n</div>\n<div class="modal-body">\n  <div class="d-flex justify-content-center">\n    <img src="http://image.sinajs.cn/newchart/v5/fundpre/min/' +
__e( code ) +
'.gif?' +
__e( r ) +
'" />\n  </div>\n</div>\n';

}
return __p
}})();
(function() {
window["JST"] = window["JST"] || {};

window["JST"]["tpl_profilobtn"] = function(obj) {
obj || (obj = {});
var __t, __p = '', __e = _.escape;
with (obj) {
__p += '    <li class="nav-item" style="display: none;">\n      <button data-pfid="' +
__e( pfid ) +
'" id="_pfbtn' +
__e( pfid ) +
'" class="btn btn-secondary btn-sm btn-block profile_btn">\n        <i class="fa fa-th-large" aria-hidden="true"></i>\n        组合' +
__e( pfid ) +
'\n      </button>\n    </li>\n';

}
return __p
}})();
(function() {
window["JST"] = window["JST"] || {};

window["JST"]["tpl_securityname"] = function(obj) {
obj || (obj = {});
var __t, __p = '', __e = _.escape, __j = Array.prototype.join;
function print() { __p += __j.call(arguments, '') }
with (obj) {
__p += '    ';
 var href;
    if(type == 'fund') { href = "http://fund.eastmoney.com/"+code+".html"; }
    else if(type == 'stock') { href = "http://quote.eastmoney.com/"+code+".html"; } ;
__p += '\n    <a href="' +
__e( href ) +
'" data-type="' +
__e( type ) +
'" data-name="' +
__e( name ) +
'" data-code="' +
__e( code ) +
'" data-toggle="modal" data-target="#chart">\n      ' +
__e( name ) +
'\n    </a>\n';

}
return __p
}})();
(function() {
window["JST"] = window["JST"] || {};

window["JST"]["tpl_stockchart"] = function(obj) {
obj || (obj = {});
var __t, __p = '', __e = _.escape, __j = Array.prototype.join;
function print() { __p += __j.call(arguments, '') }
with (obj) {
__p += '    ';
 var r=Math.random(); ;
__p += '\n    <div class="modal-header">\n      <h4 class="modal-title"><a href="http://quote.eastmoney.com/' +
__e( code ) +
'.html" target="_blank">' +
__e( name ) +
'</a></h4>\n      <button type="button" class="close" data-dismiss="modal" aria-label="Close">\n        <span aria-hidden="true">&times;</span>\n      </button>\n    </div>\n    <div class="modal-body">\n      <div class="d-flex justify-content-center"><img src="http://image.sinajs.cn/newchart/min/n/' +
__e( code ) +
'.gif?' +
__e( r ) +
'" /></div>\n      <div class="d-flex justify-content-center"><img src="http://image.sinajs.cn/newchart/daily/n/' +
__e( code ) +
'.gif?' +
__e( r ) +
'" /></div>\n    </div>\n';

}
return __p
}})();
//# sourceMappingURL=js_templates-debug.js.map
