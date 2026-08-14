(function(global){
  'use strict';
  const entities={'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'};
  global.TradingHelperSecurity=Object.freeze({
    escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,char=>entities[char])}
  });
})(window);
