console.log('HII')

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    console.log(sender.tab ?
                "from a content script:" + sender.tab.url :
                "from the extension");
    if (request.greeting === "hello")
      sendResponse({farewell: "goodbye"});
  }
);

const getFromWebPage = async () => {
  const [tab] = await chrome.tabs.query({ active: true });
  console.log(tab)
  const response = await chrome.tabs.sendMessage(tab.id, {greeting: "hello"});
  console.log(response);
}

const getRates = async ()=> {
  console.log('Hii Rates')
  await getFromWebPage()
}

document.getElementById("getrates").addEventListener("click", getRates);

