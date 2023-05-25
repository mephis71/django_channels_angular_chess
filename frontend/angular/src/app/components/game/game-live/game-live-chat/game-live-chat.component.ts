import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { GameChatService } from 'src/app/services/game-chat.service';
import { ChatMessage } from 'src/app/models/ws-messages';
import { Subscription } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { User } from 'src/app/models/user';

@Component({
  selector: 'game-live-chat',
  templateUrl: './game-live-chat.component.html',
  styleUrls: ['./game-live-chat.component.css']
})
export class GameLiveChatComponent implements OnInit, OnDestroy {
  @Input() user: User;
  chatWsSub: Subscription;
  chatWsSubjectSub: Subscription;

  messages: ChatMessage[] = [];
  chatMessageInput: string;
  
  constructor(
    private chatService: GameChatService,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.chatWsSubjectSub = this.chatService.chatWsObservableReady.subscribe({
      next: () => {
        this.chatWsSub = this.getChatWsSub()
      }
    })

    this.route.params.subscribe(params => {
      const path = `game/live/${params['id']}/chat`
      this.chatService.openChatWebSocket(path);
    })
  }

  ngOnDestroy(): void {
    this.chatService.closeWebSocket()
    const subs = [this.chatWsSub, this.chatWsSubjectSub]
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
    if(this.chatMessageInput && this.user) {
      const msg = new ChatMessage(this.user.username, this.chatMessageInput);
      this.chatService.sendChatMsg(msg);
      this.chatMessageInput = '';
    }
  }
  
}
