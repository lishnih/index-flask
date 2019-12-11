// stan 2018-08-04


const preLog = document.querySelector('pre#debug');

function debug(text) {
  if (preLog)
    preLog.textContent += ('\n' + text);
  else
    console.log(text);
}


function trace(arg) {
  const now = (window.performance.now() / 1000).toFixed(3)
  console.log(`${now}: `, arg);
}


function serializeObject(selector) {
  var form = document.querySelector(selector);
  var formArray = form.serializeArray();

  var formData = {};
  for(var i = 0, n = formArray.length; i < n; ++i)
    formData[formArray[i].name] = formArray[i].value;

  return formData;
};
