// get all the love and hate buttons
const loveButtons = document.querySelectorAll('.love-btn');
const hateButtons = document.querySelectorAll('.hate-btn');

// current date without the time
const getCurrentDate = () => {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return now.toISOString();
};

// event listeners to love buttons
loveButtons.forEach(loveBtn => {
  loveBtn.addEventListener('click', () => {
    // parent card body element
    const cardBody = loveBtn.closest('.card-body');

    // score element
    const scoreElement = cardBody.querySelector('.score');

    // check if the score element is found
    if (scoreElement) {
      // current score value - might need to fix types, also prep it in case it's null
      let score = parseInt(scoreElement.textContent);

      // check if the button has already been clicked today
      const lastClickDate = localStorage.getItem(`loveBtnClickDate_${scoreElement.dataset.rank}`);
      if (lastClickDate !== getCurrentDate()) {
        // increment score
        score += 1;

        // update score element
        scoreElement.textContent = score;

        // store current date as the last click date
        localStorage.setItem(`loveBtnClickDate_${scoreElement.dataset.rank}`, getCurrentDate());

        // disable the button after clicking once
        loveBtn.disabled = true;

        // get studentId from the hidden div's content
        const studentID = cardBody.querySelector('.studentID').id;

        // create a new FormData object to send data in the POST request
        const formData = new FormData();
        formData.append('rating_type', 'love');
        formData.append('student_id', studentID);

        // send a POST request to the /rate endpoint
        fetch('/rate', {
          method: 'POST',
          body: formData
        })
        .then(function(response) {
          if (response.ok) {
            // Handle success response
            console.log('Love rating added successfully!');
          } else {
            // Handle error response
            console.error('Error adding love rating:', response.statusText);
          }
        })
        .catch(function(error) {
          // Handle any network or other errors
          console.error('Error adding love rating:', error);
        });
      } else {
        // alert the user that they've already clicked the button today
        alert('You have already clicked this button today!');
      }
    }
  });
});

// event listeners to hate buttons
hateButtons.forEach(hateBtn => {
    hateBtn.addEventListener('click', () => {
      // parent card body element
      const cardBody = hateBtn.closest('.card-body');
  
      // score element
      const scoreElement = cardBody.querySelector('.score');
  
      // check if the score element is found
      if (scoreElement) {
        // current score value - might need to fix types, also prep it in case it's null
        let score = parseInt(scoreElement.textContent);
  
        // check if the button has already been clicked today
        const lastClickDate = localStorage.getItem(`hateBtnClickDate_${scoreElement.dataset.rank}`);
        if (lastClickDate !== getCurrentDate()) {
          // decrement score
          score -= 1;
  
          // update score element
          scoreElement.textContent = score;
  
          // store current date as the last click date
          localStorage.setItem(`hateBtnClickDate_${scoreElement.dataset.rank}`, getCurrentDate());
  
          // disable the button after clicking once
          hateBtn.disabled = true;
  
          // get studentId from the hidden div's content
          const studentID = cardBody.querySelector('.studentID').id;
  
          // create a new FormData object to send data in the POST request
          const formData = new FormData();
          formData.append('rating_type', 'hate');
          formData.append('student_id', studentID);
  
          // send a POST request to the /rate endpoint
          fetch('/rate', {
            method: 'POST',
            body: formData
          })
          .then(function(response) {
            if (response.ok) {
              // Handle success response
              console.log('Hate rating added successfully!');
            } else {
              // Handle error response
              console.error('Error adding hate rating:', response.statusText);
            }
          })
          .catch(function(error) {
            // Handle any network or other errors
            console.error('Error adding hate rating:', error);
          });
        } else {
          // alert the user that they've already clicked the button today
          alert('You have already clicked this button today!');
        }
      }
    });
  });

// handle new student form
document.getElementById('studentForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent form submission
  
  // get form data
  var formData = new FormData(event.target);
  
  // send POST request
  fetch('/new-student', {
    method: 'POST',
    body: formData
  })
  .then(function(response) {
    if (response.ok) {
      console.log('Student added successfully');
    } else {
      console.error('Error:', response.statusText);
    }
  })
  .catch(function(error) {
    console.error('Error:', error);
  });
});