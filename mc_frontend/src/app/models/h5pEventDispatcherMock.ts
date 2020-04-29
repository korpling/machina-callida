import {XAPIevent} from './xAPIevent';
import Result from './xAPI/Result';
import StatementBase from './xAPI/StatementBase';
import Verb from './xAPI/Verb';

export default class H5PeventDispatcherMock {
    listeners: { [eventName: string]: any[] } = {};

    public on(eventName: string, callback: any) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
    }

    public trigger(eventName: string, event: any) {
        this.listeners[eventName].forEach(value => value(event));
    }

    public triggerXAPI(verb: string, result: Result) {
        this.trigger('xAPI', new XAPIevent({
            data: {
                statement: new StatementBase({
                    result,
                    verb: new Verb({id: verb})
                })
            }
        }));
    };
}
