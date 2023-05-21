import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { GameChatService } from 'src/app/services/game-chat.service';
import { ChatMessage } from 'src/app/models/chat_message';
import { Subscription } from 'rxjs';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'game-live-chat',
  templateUrl: './game-live-chat.component.html',
  styleUrls: ['./game-live-chat.component.css']
})
export class GameLiveChatComponent implements OnInit, OnDestroy {
  chatWsSub: Subscription;
  chatWsSubjectSub: Subscription;

  messages: ChatMessage[] = [];
  message_form: FormGroup;
  
  constructor(
    private chatService: GameChatService,
    private formBuilder: FormBuilder,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.chatWsSubjectSub = this.chatService.chatWsObservableReady.subscribe({
      next: () => {
        this.chatWsSub = this.getChatWsSub()
      }
    })

    this.message_form = this.formBuilder.group({
      text: null,
    })

    this.route.params.subscribe(params => {
      let path = `game/live/${params['id']}/chat`
      this.chatService.openChatWebSocket(path);
    })
  }

  ngOnDestroy(): void {
    this.chatService.closeWebSocket()
    let subs = [this.chatWsSub, this.chatWsSubjectSub]
    for(let sub of subs) {
      if(sub) {
        sub.unsubscribe()
      }
    }
  }

  getChatWsSub(): Subscription {
    return this.chatService.chatWsObservable.subscribe({
      next: data => {
        this.messages.push(data);
      }
    });
  }

  sendChatMessage() {
    let msg = this.message_form.getRawValue()
    if(msg.text) {
      this.chatService.sendMsg(msg)
      this.message_form.reset()
    }
  }

}
