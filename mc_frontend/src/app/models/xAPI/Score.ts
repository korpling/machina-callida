class Score {
    max: number;
    min: number;
    raw: number;
    scaled: number;

    constructor(init?: Partial<Score>) {
        Object.assign(this, init);
    }
}

export default Score;
