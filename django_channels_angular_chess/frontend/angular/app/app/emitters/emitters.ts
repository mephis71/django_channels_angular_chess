import { EventEmitter } from "@angular/core";

export class Emitters {
    static usernameEmitter = new EventEmitter<string | null>();
}