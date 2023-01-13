import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { ChatMessage } from '../models/chat_message';
import { GameChatService } from '../services/game-chat.service';

@Component({
  selector: 'app-game-chat',
  templateUrl: './game-chat.component.html',
  styleUrls: ['./game-chat.component.css']
})
export class GameChatComponent implements OnInit {
  message_form: FormGroup;

  constructor(
    public chatService: GameChatService,
    private formBuilder: FormBuilder,
  ) { }

  ngOnInit(): void {
    this.message_form = this.formBuilder.group({
      text: null,
    })
    this.chatService.clearVariables()
    this.chatService.openWebSocket()
  }

  sendChatMessage() {
    let msg = this.message_form.getRawValue()
    if(msg.text) {
      this.chatService.sendMsg(msg)
      this.message_form.reset()
    }
  }

}
