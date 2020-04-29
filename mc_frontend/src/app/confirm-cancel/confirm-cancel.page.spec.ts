import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ConfirmCancelPage} from './confirm-cancel.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';

describe('ConfirmCancelPage', () => {
    let confirmCancelPage: ConfirmCancelPage;
    let fixture: ComponentFixture<ConfirmCancelPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ConfirmCancelPage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ConfirmCancelPage);
        confirmCancelPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(confirmCancelPage).toBeTruthy();
    });

    it('should confirm', () => {
        confirmCancelPage.helperService.currentPopover = {dismiss: () => Promise.resolve(true)} as HTMLIonPopoverElement;
        spyOn(confirmCancelPage.helperService, 'goToHomePage').and.returnValue(Promise.resolve(true));
        confirmCancelPage.confirm();
        expect(confirmCancelPage.helperService.currentPopover).toBeFalsy();
    });
});
