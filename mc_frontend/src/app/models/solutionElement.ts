export class SolutionElement {
    public sentence_id: number;
    public token_id: number;
    public content: string;
    public salt_id: string;

    constructor(init?: Partial<SolutionElement>) {
        Object.assign(this, init);
    }
}