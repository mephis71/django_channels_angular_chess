import { Injectable } from '@angular/core';
import { ChatMessage } from '../models/chat_message';

@Injectable({
  providedIn: 'root'
})
export class GameChatService {

  ws: WebSocket;
  messages: ChatMessage[] = [];

  constructor() { }

  public openWebSocket() {
    let path = window.location.pathname;

    this.ws = new WebSocket(`ws://localhost:8000${path}/chat`);

    this.ws.onopen = (event) => {

    };
    this.ws.onmessage = (event) => {
      var msg = JSON.parse(event.data)
      this.messages.push(msg)
    };
    this.ws.onclose = (event) => {

    };
  }

  public closeWebSokcet() {
    this.ws.close();
  }

  public sendMsg(msg:any) {
    this.ws.send(JSON.stringify(msg))
  }

  clearVariables() {
    this.messages = [];
  }
}
