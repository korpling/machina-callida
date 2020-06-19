import {EventMC} from './enum';

export default class EventRegistry {
    listeners: { [eventName: string]: any[] } = {};

    public off(eventName: EventMC) {
        this.listeners[eventName] = [];
    }

    public on(eventName: EventMC, callback: any) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
    }

    public trigger(eventName: EventMC, event: any) {
        if (this.listeners[eventName]) {
            this.listeners[eventName].forEach(value => value(event));
        }
    }
}
