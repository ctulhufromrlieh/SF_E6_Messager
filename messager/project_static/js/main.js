const urlGetChatUserList = 'http://127.0.0.1:8000/chat_users/get_list/'
const urlGetChatRoomList = 'http://127.0.0.1:8000/chat_rooms/get_list/'

let socket
let selectedDest = -1
let selectedId = -1
let selectedElem = null

function init_user_list(){
  fetch(urlGetChatUserList)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    refreshUserList(data)
    // changeProfile(1, '123')
  })
  .catch(() => {
    console.log('init_user_list error') 
  });
}

function init_room_list(){
  fetch(urlGetChatRoomList)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    refreshRoomList(data)
  })
  .catch(() => {
    console.log('init_room_list error') 
  });
}

function deselectElem(elem){
  if (!elem){
    return
  }

  elem.classList.remove('selected-elem')

  // if (elem.className.includes('user-elem')){
  //   elem.className = 'user-elem'  
  // } else if (elem.className.includes('room-elem')){
  //   elem.className = 'room-elem'  
  // } 
}

function select(dest, id, elem){
  deselectElem(selectedElem)
  if (dest == 0){
    // elem.ClassName = 'user-elem selected-elem'
    elem.classList.add('selected-elem')
  } else if (dest == 1){
      // elem.ClassName = 'room-elem selected-elem'
      elem.classList.add('selected-elem')
  }
  else{
    selectedDest = dest
    selectedId = id
    selectedElem = elem
    return
  }

  selectedDest = dest
  selectedId = id
  selectedElem = elem
}

function deleteElementsOfClass(className){
  let userElems = document.getElementsByClassName(className)
  for (let currUserElem of userElems){
    currUserElem.remove()
  }
}

function createUserElem(id, username){
  let newElem = document.createElement("div");
  newElem.className = 'user-elem'
  newElem.textContent = `${username} (id = ${id})`
  newElem.id = `user-elem-${id}`
  newElem.addEventListener('click', (event) => {
    select(0, id, newElem)
  })

  return newElem
}

function createRoomElem(id, name){
    let newElem = document.createElement("div");
    newElem.className = 'room-elem'
    newElem.textContent = `${name} (id = ${id})`
    newElem.id = `room-elem-${id}`
    newElem.addEventListener('click', (event) => {
      select(1, id, newElem)
    })

    return newElem
}

function refreshUserList(users){
  pnlUsers = document.getElementsByClassName('users-panel')[0]

  deleteElementsOfClass('user-elem')

  // users.forEach((currUser) => {
  //   let newElem = document.createElement("div");
  //   newElem.className = 'user-elem'
  //   newElem.textContent = `${currUser.username} (id = ${currUser.id})`
  //   newElem.id = `user-elem-${currUser.id}`
  //   newElem.addEventListener('click', (event) => {
  //     select(0, currUser.id, newElem)
  //   })
  //   pnlUsers.append(newElem)
  // })

  users.forEach((currUser) => {
    // let newElem = document.createElement("div");
    // newElem.className = 'user-elem'
    // newElem.textContent = `${currUser.username} (id = ${currUser.id})`
    // newElem.id = `user-elem-${currUser.id}`
    // newElem.addEventListener('click', (event) => {
    //   select(0, currUser.id, newElem)
    // })
    let newElem = createUserElem(currUser.id, currUser.username)
    pnlUsers.append(newElem)
  })

  // for (let currUser of users){
  //   let newElem = document.createElement("div");
  //   newElem.className = 'user-elem'
  //   newElem.textContent = `${currUser.username} (id = ${currUser.id})`
  //   newElem.addEventListener('click', (event) => {
  //     select(0, currUser.id, newElem)
  //   })
  //   pnlUsers.append(newElem)
  // }
}

function refreshRoomList(rooms){
  pnlRooms = document.getElementsByClassName('rooms-panel')[0]
  
  deleteElementsOfClass('room-elem')

  rooms.forEach((currRoom) => {
    // let newElem = document.createElement("div");
    // newElem.className = 'room-elem'
    // newElem.textContent = `${currRoom.name} (id = ${currRoom.id})`
    // newElem.id = `room-elem-${currRoom.id}`
    // newElem.addEventListener('click', (event) => {
    //   select(1, currRoom.id, newElem)
    // })
    let newElem = createRoomElem(currRoom.id, currRoom.name)
    pnlRooms.append(newElem)
  })

  // for (let currRoom of rooms){
  //   let newElem = document.createElement("div");
  //   newElem.className = 'room-elem'
  //   newElem.textContent = `${currRoom.name} (id = ${currRoom.id})`
  //   newElem.addEventListener('click', (event) => {
  //     select(1, currRoom.id, newElem)
  //   })
  //   pnlRooms.append(newElem)
  // }
}

function addProfile(id, username){
  const pnlUsers = document.getElementsByClassName('users-panel')[0]
  const lastUser = pnlUsers.children[pnlUsers.children.length - 1]
  newElem = createUserElem(id, username)
  lastUser.after(newElem)
}

function changeProfile(id, username){
  let elemId = `user-elem-${id}`
  console.log(elemId)
  let userElem = document.getElementById(elemId)
  console.log(userElem)
  console.log(document.getElementById(elemId))
  let prevUser = userElem.previousSibling
  userElem.remove()
  if (prevUser){
    prevUser.after(createUserElem(id, username))
  } else {
    addProfile(id, username)
  }
  
  newElem = createUserElem(id, username)
  lastUser.after(newElem)
}

function message_handler(data_text){
  console.log(data_text)
  data = JSON.parse(data_text)
  if (data.msg_type == 'user_list'){
    // refreshUserList(data.list)
  } else if (data.msg_type == 'room_list'){
    // refreshRoomList(data.list)
  } else if (data.msg_type == 'profile_created'){
    addProfile(data.id, data.username)
  } else if (data.msg_type == 'profile_changed'){
    changeProfile(data.id, data.username)
  }else{
    // console.log(data_text)
  }

}

function initialize(){
  socket = new WebSocket('ws://127.0.0.1:8000/ws');

  init_user_list()
  init_room_list()

  socket.onopen = function(e) {
    // socket.send(JSON.stringify({
    //   message: 'Hello from Js client'
    // }));
    // socket.send(JSON.stringify({
    //   get: 'user_list'
    // }));
    // socket.send(JSON.stringify({
    //   get: 'room_list'
    // }));
  };

  socket.onmessage = function(event) {
    message_handler(event.data)
    // console.log(event.data)
  //   try {
  //     console.log(event);
  //   } catch (e) {
  //     console.log('Error:', e.message);
  //   }
  };
}

window.onload = initialize