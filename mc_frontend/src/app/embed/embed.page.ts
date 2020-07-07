import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ExerciseService} from '../exercise.service';
import {ExerciseParams} from '../models/exerciseParams';
import {rejects} from 'assert';

@Component({
    selector: 'app-embed',
    templateUrl: './embed.page.html',
    styleUrls: ['./embed.page.scss'],
})
export class EmbedPage implements OnInit {

    constructor(public activatedRoute: ActivatedRoute,
                public exerciseService: ExerciseService) {
    }

    loadExercise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.activatedRoute.queryParams.subscribe((params: ExerciseParams) => {
                this.exerciseService.loadH5P(params.eid).then(() => {
                    return resolve();
                }, () => {
                    return reject();
                });
            });
        });
    }

    ngOnInit(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.loadExercise().then(() => {
                return resolve();
            }, () => {
                return reject();
            });
        });
    }

}
