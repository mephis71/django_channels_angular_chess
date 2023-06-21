import { AfterViewInit, Component, ElementRef, Input, OnDestroy, OnInit, Renderer2 } from '@angular/core';
import { GameChatService } from 'src/app/services/game-chat.service';
import { ChatMessage } from 'src/app/models/ws-messages';
import { Subscription } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { CssService } from 'src/app/services/css.service';

@Component({
  selector: 'game-live-chat',
  templateUrl: './game-live-chat.component.html',
  styleUrls: ['./game-live-chat.component.css']
})
export class GameLiveChatComponent implements OnInit, OnDestroy, AfterViewInit {
  @Input() username: string;
  chatWsSub: Subscription;
  chatWsSubjectSub: Subscription;

  messages: ChatMessage[] = [];
  chatMessageInput: string;
  
  constructor(
    private chatService: GameChatService,
    private route: ActivatedRoute,
    private el: ElementRef,
    private cssService: CssService,
    private renderer: Renderer2
  ) { }

  ngAfterViewInit(): void {
    let el = document.getElementById('chat-bar')
    this.cssService.boardHeightBroadcast.subscribe({
      next: height => {
        if (window.innerWidth >= 768) {
          this.renderer.setStyle(el, 'max-height', `${height}px`)
        }
        else {
          this.renderer.setStyle(el, 'max-height', '34vh')
        }
      }
    })
  }  

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
    if(this.chatMessageInput && this.username) {
      const msg = new ChatMessage(this.username, this.chatMessageInput);
      this.chatService.sendChatMsg(msg);
      this.chatMessageInput = '';
    }
  }
  
}
