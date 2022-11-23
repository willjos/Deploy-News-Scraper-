window.onload = async function load() {
  getStories()
  document
    .getElementById('submit-search')
    .addEventListener('click', onSearchClick)
}

function onSearchClick() {
  const searchInputText = document.getElementById('search').value

  return
}

async function getStories() {
  const window_url = window.location.href
  const res = await fetch(`http://18.132.245.84/stories`, {
    method: 'GET',
    credentials: 'include'
  })
  const data = await res.json()

  displayStories(data.stories)
}

async function handleVote(e) {
  const elemID = e.target.id.split('-')
  const id = elemID[0]
  const direction = elemID[1]
  const window_url = window.location.href
  const rawRes = await fetch(`http://18.132.245.84/stories/${id}/votes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction }),
    credentials: 'include'
  })
  // const res = await rawRes.json() //commented this out and now it auto-reloads...
  location.reload()
}

function displayStories(stories) {
  stories.forEach(createStory)
}

function createStory(story) {
  const stories = document.getElementById('stories')
  const storyWrapper = document.createElement('div')
  let pluralS = ''
  if (story.score !== 1) {
    pluralS = 's'
  }
  if (story.score === null) {
    story.score = 0
  }
  storyWrapper.innerHTML = `
  <hr />
	<p>
		<a class="title" href=${story.url}>${story.title} </a>
		<span>(${story.score} point${pluralS})</span>
  
	</p>`

  const upvoteButton = createVoteButton('upvote', `${story.id}-up`, '⬆')
  const downvoteButton = createVoteButton('downvote', `${story.id}-down`, '⬇')

  storyWrapper.append(upvoteButton, downvoteButton)
  stories.append(storyWrapper)
}

function createVoteButton(className, id, text) {
  const button = document.createElement('button')
  button.id = id
  button.className = className
  button.addEventListener('click', handleVote)
  button.innerText = text
  return button
}
