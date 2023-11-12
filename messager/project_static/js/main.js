const urlGetChatUserList = 'http://127.0.0.1:8000/chat_users/get_list/'
const urlGetChatRoomList = 'http://127.0.0.1:8000/chat_rooms/get_list/'
// const urlSelectChat      = 'http://127.0.0.1:8000/select_chat'

let socket
let myProfileId = -1
let selectedDest = -1
let selectedId = -1
let selectedElem = null

function deselectElem(elem){
  if (!elem){
    return
  }

  elem.classList.remove('selected-elem')
}

function select(dest, id, elem){
  // deselectElem(selectedElem)
  // if (dest == 0){
  //   elem.classList.add('selected-elem')
  // } else if (dest == 1){
  //     elem.classList.add('selected-elem')
  // }
  // else{
  //   selectedDest = dest
  //   selectedId = id
  //   selectedElem = elem
  //   return
  // }

  let url = `http://127.0.0.1:8000/chat_select/${dest}/${id}/`

  fetch(url)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    // change on client if success
    console.log(data)

    deleteElementsOfClass("message-elem")
    for (currMessage of data.messages){
      addMessage(currMessage.username, currMessage.text)
    }

    deselectElem(selectedElem)
    if (dest == 0){
      elem.classList.add('selected-elem')
    } else if (dest == 1){
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
  })
  .catch(() => {
    console.log('select error') 
  });

  // selectedDest = dest
  // selectedId = id
  // selectedElem = elem
}

function init_user_list(){
  fetch(urlGetChatUserList)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    refreshUserList(data.list, data.me)
    init_room_list()
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

function messageCreateChatRoom(name){  
  let url = `http://127.0.0.1:8000/chat_rooms/create/${name}/`

  fetch(url)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    console.log(data)
  })
  .catch(() => {
    console.log('messageCreateChatRoom error') 
  });
}

function messageChangeChatRoom(id, name){  
  let url = `http://127.0.0.1:8000/chat_rooms/change/${id}/${name}/`

  fetch(url)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    console.log(data)
    // alert(name)
  })
  .catch(() => {
    console.log('messageChangeChatRoom error') 
  });
}

function messageDeleteChatRoom(id){  
  let url = `http://127.0.0.1:8000/chat_rooms/delete/${id}`

  fetch(url)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    console.log(data)
  })
  .catch(() => {
    console.log('messageDeleteChatRoom error') 
  });
}

function deleteElementsOfClass(className){
  let userElems = document.getElementsByClassName(className)
  for (let currUserElemIndex = userElems.length - 1;currUserElemIndex >= 0; currUserElemIndex--){
    userElems[currUserElemIndex].remove()
  }
  // for (let currUserElem of userElems){
    // currUserElem.remove()
  // }
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

function getInnerHTMLForRoomElem(id, name, owner_id){
  if (owner_id == myProfileId){
      return `<input type="text" id="room-elem-name-${id}" value="${name}" /><input type="button" id="room-elem-change-${id}" value="Изменить"/><input type="button" id="room-elem-delete-${id}" value="Удалить" />`
  }else{
    return `${name} (id = ${id})`
  }
}

function createRoomElem(id, name, owner_id){
    let newElem = document.createElement("div");
    newElem.className = 'room-elem'
    newElem.innerHTML = getInnerHTMLForRoomElem(id, name, owner_id)
    // newElem.textContent = `${name} (id = ${id})`
    newElem.id = `room-elem-${id}`
    
    newElem.addEventListener('click', (event) => {
      select(1, id, newElem)
    })

    console.log(newElem.children)

    if (owner_id == myProfileId){
      // let btnChange = document.getElementById(`room-elem-change-${id}`)
      // let btnChange = newElem.getElementById(`room-elem-change-${id}`)
      let btnChange = newElem.children[1]
      btnChange.addEventListener('click', (event) => {
        // let edtName = document.getElementById(`room-elem-name-${id}`)
        // let edtName = newElem.getElementById(`room-elem-name-${id}`)
        let edtName = newElem.children[0]
        messageChangeChatRoom(id, edtName.value)
      })

      // let btnDelete = document.getElementById(`room-elem-delete-${id}`)
      // let btnDelete = newElem.getElementById(`room-elem-delete-${id}`)
      let btnDelete = newElem.children[2]
      btnDelete.addEventListener('click', (event) => {
        messageDeleteChatRoom(id)
      })
    }

    return newElem
}

function refreshUserList(users, me){
  pnlUsers = document.getElementsByClassName('users-panel')[0]

  deleteElementsOfClass('user-elem')

  users.forEach((currUser) => {
    let newElem = createUserElem(currUser.id, currUser.username)
    pnlUsers.append(newElem)
  })
  myProfileId = me.id
  refreshTitle(myProfileId, me.username)
}

function refreshRoomList(rooms){
  pnlRooms = document.getElementsByClassName('rooms-panel')[0]
  
  deleteElementsOfClass('room-elem')

  rooms.forEach((currRoom) => {
    let newElem = createRoomElem(currRoom.id, currRoom.name, currRoom.owner_id)
    pnlRooms.append(newElem)
  })


}

function addProfile(id, username){
  const pnlUsers = document.getElementsByClassName('users-panel')[0] 
  newElem = createUserElem(id, username)

  if (pnlUsers.children.length > 0) {
    const lastUser = pnlUsers.children[pnlUsers.children.length - 1]
    lastUser.after(newElem)
  } else {
    pnlUsers.append(newElem)
  }
  
}

function refreshTitle(id, username){
  let userElem = document.querySelector("header")
  userElem.textContent = `Добро пожаловать, ${username}.`
}

function changeProfile(id, username){
  let elemId = `user-elem-${id}`
  console.log(elemId)
  let userElem = document.getElementById(elemId)
  if (userElem){
    console.log(userElem)
    console.log(document.getElementById(elemId))
    let prevUser = userElem.previousSibling
    userElem.remove()
    if (prevUser){
      prevUser.after(createUserElem(id, username))
    } else {
      addProfile(id, username)
    }

    // newElem = createUserElem(id, username)
    // lastUser.after(newElem)
  } else if (myProfileId == id) {
    refreshTitle(myProfileId, username)
  }
}

function createChatRoom(id, name, owner_id){
  let pnlRooms = document.getElementsByClassName('rooms-panel')[0]  
  let newElem = createRoomElem(id, name, owner_id)
  pnlRooms.append(newElem)
}

function changeChatRoom(id, name, owner_id){
  let chatRoomElem = document.getElementById(`room-elem-${id}`)
  if (chatRoomElem){
    let pnlRoomElems = chatRoomElem.parentElement
    let nextRoomElem = chatRoomElem.nextSibling
    chatRoomElem.remove()
    let newElem = createChatRoom(id, name, owner_id)
    if (nextRoomElem){
      nextRoomElem.before(newElem)
    }else{
      pnlRoomElems.append(newElem)  
    }

  }
  // if (chatRoomElem){
  //   chatRoomElem.innerHTML = getInnerHTMLForRoomElem(id, name, owner_id)
  //   // chatRoomElem.textContent = `${name} (id = ${id})`
  // }
}

function deleteChatRoom(id, name, owner_id){
  let chatRoomElem = document.getElementById(`room-elem-${id}`)
  if (chatRoomElem){
    chatRoomElem.remove()
  }  
}

function addMessage(username, text){
  let pnlMessages = document.getElementsByClassName('messages-panel')[0]
  let newElem = document.createElement("div");
  newElem.className = 'message-elem'
  newElem.innerHTML = `<b>${username}</b>: ${text}`
  pnlMessages.append(newElem)
  // newElem.id = `user-elem-${id}`
  // newElem.addEventListener('click', (event) => {
    // select(0, id, newElem)
  // })

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
  } else if (data.msg_type == 'message_created'){
    addMessage(data.username, data.text)
  } else if (data.msg_type == "chatroom_created") {
    createChatRoom(data.id, data.name, data.owner_id)
  } else if (data.msg_type == "chatroom_changed") {
    changeChatRoom(data.id, data.name, data.owner_id)
  } else if (data.msg_type == "chatroom_deleted") {
    deleteChatRoom(data.id, data.name, data.owner_id)
  }else{
    // console.log(data_text)
  }

}

function initialize(){
  btnSend = document.getElementById('message-editor-send')
  btnSend.addEventListener('click', (event) => {
    let editor = document.getElementById('message-editor')
    socket.send(JSON.stringify({
       post: 'send_message',
       text: editor.value
     }));    

     editor.value = ''
  })

  socket = new WebSocket('ws://127.0.0.1:8000/ws');

  init_user_list()
  // init_room_list()

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
  };
}

window.onload = initialize