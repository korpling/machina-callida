export class Feedback {
    public correct: string;
    public incorrect: string;
    public partiallyCorrect: string;
    public general: string;
    constructor(init?: Partial<Feedback>) {
        Object.assign(this, init);
    }
}

