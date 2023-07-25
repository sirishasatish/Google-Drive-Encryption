// """/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// // Authors:
// //		Dasari, Veera Venkata Sairam: VXD210027
//         Gnanamoorthy, Vijayan: VXG210040
//         Mulkalwar, Ashray: AXM190211
//         Satish, Sirisha: SXS210095
//         Vunnava, Vaishnavi: VXV210027

// // Created date : 4/20/2023
// // Description : Google Drive Python file 
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// """


var secretKey;
function strToByteArray(str) {
    const buffer = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i++) {
        buffer[i] = str.charCodeAt(i);
    }
    return buffer;
}

function byteArrayToStr(arr) {
    return String.fromCharCode.apply(this, arr);
}

function sharedKeys(shares) {
    const splitResults = document.querySelector('#share-results');
    while (splitResults.firstChild) {
        splitResults.removeChild(splitResults.firstChild);
    }

    splitResults.appendChild(document.createElement('hr'));
    for (let i = 0; i < shares.length; i++) {
        const shareBase64 = window.btoa(byteArrayToStr(shares[i]));

        const label = document.createElement('span');
        label.textContent = `Secret share ${i + 1}: `;

        const value = document.createElement('code');
        value.textContent = shareBase64;

        const element = document.createElement('p');
        element.appendChild(label);
        element.appendChild(value);

        splitResults.appendChild(element);
    }
}

function showFetchBoxes(m) {
    const combineInputs = document.querySelector('#fetch-inputs');
    while (m < combineInputs.childNodes.length) {
        combineInputs.removeChild(combineInputs.lastChild);
    }
    for (let i = combineInputs.childNodes.length; i < m; i++) {
        const label = document.createElement('label');
        label.setAttribute('for', `SecretShare-${i + 1}`);
        label.textContent = `Secret Share ${i + 1} : `;

        const value = document.createElement('textarea');
        value.setAttribute('name', `SecretShare-${i + 1}`);
        value.setAttribute('rows', 1);

        const element = document.createElement('p');
        element.appendChild(label);
        element.appendChild(value);

        combineInputs.appendChild(element);
    }
}

function showFetchResult(secret) {
    const fetchResult = document.querySelector('#fetch-result');

    while (fetchResult.firstChild) {
        fetchResult.removeChild(fetchResult.firstChild);
    }

    fetchResult.appendChild(document.createElement('hr'));

    const label = document.createElement('span');
    label.textContent = `Secret: `;

    const value = document.createElement('code');
    value.textContent = byteArrayToStr(secret);

    const element = document.createElement('p');
    element.appendChild(label);
    element.appendChild(value);
     secretKey=  byteArrayToStr(secret);
     showFile();
     fetchResult.appendChild(element);
}

function showShareScreen() {
    const splitForm = document.querySelector('#share-form');
    splitForm.addEventListener('submit', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const n = splitForm.querySelector('input[name=users]')
        const numUsers = Number.parseInt(n.value);

        const s = splitForm.querySelector('input[name=shares]')
        const numShares = Number.parseInt(s.value);

        const sec = splitForm.querySelector('textarea[name=secret]')
        const secret = sec.value;

        const shares = shamirs.split(strToByteArray(secret), numUsers, numShares);

        sharedKeys(shares);
    });
}

function showFetchScreen() {
    const fetchForm = document.querySelector('#fetch-form');

    const numberUser = fetchForm.querySelector('input[name=users]');
    const updateFetchBoxes = () => showFetchBoxes(Number.parseInt(numberUser.value));
    numberUser.addEventListener('change', updateFetchBoxes);
    updateFetchBoxes();

    fetchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const users = Number.parseInt(fetchForm.querySelector('input[name=users]').value);
        const shares = [];
        for (let i = 0; i < users; i++) {
            const shareBase64 = fetchForm.querySelector(`textarea[name=SecretShare-${i + 1}]`).value;
            const share = strToByteArray(window.atob(shareBase64));
            shares.push(share);
        }

        const secret = shamirs.combine(shares);

        showFetchResult(secret);
    });
}

window.addEventListener('load', () => {
    showShareScreen();
    showFetchScreen();
});