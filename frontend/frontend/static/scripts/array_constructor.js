function createTwoDemensionalArray() {
    let numInArr = document.getElementById('length').value;
    let numInRow = document.getElementById('quantity').value;
  const arr = [...Array(numInArr + 1).keys()].slice(1);
  const resultArr = [];

  for (let i = 0; i <= arr.length; i++) {
    while (arr.length >= numInRow) {
      try {
        resultArr.push(arr.splice(0, numInRow));
      } catch (err) {
        console.log(err);
      }
    }
  }

  if (arr.length < numInRow && arr.length > 0) {
    resultArr.push(arr);
  }

   document.getElementById('result_multi').innerHTML = resultArr;
}

const a = createTwoDemensionalArray;
