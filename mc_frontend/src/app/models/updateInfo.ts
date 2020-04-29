export class UpdateInfo {
    public corpora: number;
    public exerciseList: number;
    constructor(init?: Partial<UpdateInfo>) {
        Object.assign(this, init);
    }
}
