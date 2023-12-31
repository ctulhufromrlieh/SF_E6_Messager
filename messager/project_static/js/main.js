const urlGetChatUserList = 'http://127.0.0.1:8000/chat_users/get_list/'
const urlGetChatRoomList = 'http://127.0.0.1:8000/chat_rooms/get_list/'
const urlSetUserData = 'http://127.0.0.1:8000/chat/set_user_data/'

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
      addMessage(currMessage.sender_id, currMessage.username, currMessage.avatar_image_url, currMessage.text)
    }

    deselectElem(selectedElem)
    if (dest == 0){
      if (elem){
      elem.classList.add('selected-elem')
      }
    } else if (dest == 1){
        if (elem){
        elem.classList.add('selected-elem')
      }
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
}

function initUserList(){
  fetch(urlGetChatUserList)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    refreshUserList(data.list, data.me)
    initRoomList()
  })
  .catch(() => {
    console.log('init_user_list error') 
  });
}

function initRoomList(){
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

function getUserAvatarImageHTML(avatar_image_url){
  if (avatar_image_url == ""){
    return "&nbsp;"
  }else{
    return `<img src="${avatar_image_url}" />`
  }
}

function messageCreateChatRoom(name){  
  // let url = `http://127.0.0.1:8000/chat_rooms/create/${name}/`
  let url = encodeURI(`http://127.0.0.1:8000/chat_rooms/create/${name}/`)
  
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
  // let url = `http://127.0.0.1:8000/chat_rooms/change/${id}/${name}/`
  let url = encodeURI(`http://127.0.0.1:8000/chat_rooms/change/${id}/${name}/`)

  fetch(url)
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    console.log(data)
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
}

function createUserElem(id, username, avatar_image_url){
  let newElem = document.createElement("div");
  newElem.className = 'user-elem'
  let avatarHTML = `<div class="avatar-elem avatar-elem-${id}">${getUserAvatarImageHTML(avatar_image_url)}</div>`
  let usernameHTML = `<span class="username-elem-${id}">${username}</span>`
  let newHTML =  avatarHTML + usernameHTML + `(id = ${id})`
  newElem.innerHTML = newHTML
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
    return `<span class="room-elem-name-${id}">${name} (id = ${id})`
  }
}

function createRoomElem(id, name, owner_id){
    let newElem = document.createElement("div");
    newElem.className = 'room-elem'
    newElem.innerHTML = getInnerHTMLForRoomElem(id, name, owner_id)
    newElem.id = `room-elem-${id}`
    
    newElem.addEventListener('click', (event) => {
      select(1, id, newElem)
    })

    // console.log(newElem.children)

    if (owner_id == myProfileId){
      let btnChange = newElem.children[1]
      btnChange.addEventListener('click', (event) => {
        let edtName = newElem.children[0]
        messageChangeChatRoom(id, edtName.value)
      })

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
    let newElem = createUserElem(currUser.id, currUser.username, currUser.avatar_image_url)
    pnlUsers.append(newElem)
  })
  myProfileId = me.id
  refreshTitle(myProfileId, me.username, me.avatar_image_url)

  let toSelectElem = null
    if (me.sel_cat == 0){
    toSelectElem = document.getElementById(`user-elem-${me.sel_chat}`)
  }else if (me.sel_cat == 1){
    toSelectElem = document.getElementById(`room-elem-${me.sel_chat}`)
  }

  select(me.sel_cat, me.sel_chat, toSelectElem)
}

function refreshRoomList(rooms){
  let pnlRoomElemAdd = document.getElementById('room-elem-add')
  
  deleteElementsOfClass('room-elem')

  rooms.forEach((currRoom) => {
    let newElem = createRoomElem(currRoom.id, currRoom.name, currRoom.owner_id)
    pnlRoomElemAdd.before(newElem)
  })
}

function addProfile(id, username, avatar_image_url){
  const pnlUsers = document.getElementsByClassName('users-panel')[0] 
  newElem = createUserElem(id, username, avatar_image_url)

  if (pnlUsers.children.length > 0) {
    const lastUser = pnlUsers.children[pnlUsers.children.length - 1]
    lastUser.after(newElem)
  } else {
    pnlUsers.append(newElem)
  }
  
}

function refreshTitle(id, username, avatar_image_url){
  let userElem = document.querySelector("#username-my")
  userElem.textContent = `${username}.`

  let avatarElem = document.querySelector("#avatar-my")
  avatarElem.innerHTML = getUserAvatarImageHTML(avatar_image_url)
}

function changeProfile(id, username, avatar_image_url){
  let nameElems = document.getElementsByClassName(`username-elem-${id}`)
  for (let currNameElem of nameElems){
    currNameElem.textContent = username
  }

  let avatarElems = document.getElementsByClassName(`avatar-elem-${id}`)
  for (let currAvatarElem of avatarElems){
    currAvatarElem.innerHTML = getUserAvatarImageHTML(avatar_image_url)
  }

  if (myProfileId == id) {
    refreshTitle(myProfileId, username, avatar_image_url)
  }
}

function createChatRoom(id, name, owner_id){
  let pnlRoomElemAdd = document.getElementById('room-elem-add')
  // let pnlRooms = document.getElementsByClassName('rooms-panel')[0]  
  let newElem = createRoomElem(id, name, owner_id)
  // pnlRooms.append(newElem)
  pnlRoomElemAdd.before(newElem)
}

function changeChatRoom(id, name, owner_id){
  let chatRoomSpans = document.querySelectorAll(`span.room-elem-name-${id}`)
  let chatRoomInputs = document.querySelectorAll(`span.room-elem-name-${id}`)

  for (let currChatRoomSpan of chatRoomSpans){
    currChatRoomSpan.textContent = name
  }
  for (let currChatRoomInput of chatRoomInputs){
    currChatRoomInput.value = name
  }  
}

function deleteChatRoom(id, name, owner_id){
  if ((selectedDest == 0) & (selectedId == id)){
    select(-1, -1, null)
  }
  let chatRoomElem = document.getElementById(`room-elem-${id}`)
  if (chatRoomElem){
    chatRoomElem.remove()
  }
}

function addMessage(sender_id, username, avatar_image_url, text){
  let pnlMessages = document.getElementsByClassName('messages-panel')[0]
  let newElem = document.createElement("div");
  
  let avatarHTML = `<div class="avatar-elem avatar-elem-${sender_id}">${getUserAvatarImageHTML(avatar_image_url)}</div>`
  let usernameHTML = `<span class="username-elem-${sender_id}">${username}</span>`
  newElem.innerHTML = avatarHTML + usernameHTML + `<span>: ${text}</span>`
  
  newElem.className = 'message-elem'
  pnlMessages.append(newElem)
}

function messageHandler(data_text){
  console.log(data_text)
  data = JSON.parse(data_text)
  if (data.msg_type == 'user_list'){
    // refreshUserList(data.list)
  } else if (data.msg_type == 'room_list'){
    // refreshRoomList(data.list)
  } else if (data.msg_type == 'profile_created'){
    addProfile(data.id, data.username, data.avatar_image_url)
  } else if (data.msg_type == 'profile_changed'){
    changeProfile(data.id, data.username, data.avatar_image_url)
  } else if (data.msg_type == 'message_created'){
    addMessage(data.sender_id, data.username, data.avatar_image_url, data.text)
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

async function uploadUserForm(){
  let nameElem = document.getElementById('user-data-name')
  let avatarElem = document.getElementById('user-data-avatar')

  let formData = new FormData();           
  formData.append("username", nameElem.value);
  formData.append("avatar_image", avatarElem.files[0]);

  await fetch(urlSetUserData, {
    method: 'POST',
    body: formData
  })
  .then((response) => {
    const result = response.json();
    return result;
  })
  .then((data) => {
    console.log(data) 
  })
  .catch(() => {
    console.log('uploadUserForm error') 
  });
}

function initialize(){
  let btnSend = document.getElementById('message-editor-send')
  btnSend.addEventListener('click', (event) => {
    let editor = document.getElementById('message-editor')
    socket.send(JSON.stringify({
       post: 'send_message',
       text: editor.value
     }));

    editor.value = ''
  })

  let btnAdd = document.getElementById('room-elem-add-btn')
  let edtAdd = document.getElementById('room-elem-add-edt')
  btnAdd.addEventListener('click', (event) => {
    messageCreateChatRoom(edtAdd.value)
  })

  socket = new WebSocket('ws://127.0.0.1:8000/ws');

  initUserList()
  
  socket.onopen = function(e) {
    // nothing
  };

  socket.onmessage = function(event) {
    messageHandler(event.data)
  };
}

window.onload = initialize