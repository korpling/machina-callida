import {IonicStorageModule} from '@ionic/storage';
import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {RouteReuseStrategy} from '@angular/router';

import {IonicModule, IonicRouteStrategy} from '@ionic/angular';
import {SplashScreen} from '@ionic-native/splash-screen/ngx';
import {StatusBar} from '@ionic-native/status-bar/ngx';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from 'src/app/app.component';
import {HttpClient, HttpClientModule} from '@angular/common/http';
import {TranslateLoader, TranslateModule} from '@ngx-translate/core';
import {HelperService} from 'src/app/helper.service';
import {ConfirmCancelPageModule} from 'src/app/confirm-cancel/confirm-cancel.module';
import {APP_BASE_HREF} from '@angular/common';

@NgModule({
    declarations: [AppComponent],
    entryComponents: [],
    imports: [
        IonicModule.forRoot(),
        BrowserModule,
        AppRoutingModule,
        IonicStorageModule.forRoot({name: 'mc_db', driverOrder: ['indexeddb', 'websql', 'localstorage']}),
        HttpClientModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useFactory: (HelperService.createTranslateLoader),
                deps: [HttpClient]
            }
        }),
        ConfirmCancelPageModule
    ],
    providers: [
        {
            provide: APP_BASE_HREF,
            useValue: window.location.pathname.split('/').slice(0, -1).join('/'),
        },
        StatusBar,
        SplashScreen,
        {provide: RouteReuseStrategy, useClass: IonicRouteStrategy},
    ],
    bootstrap: [AppComponent],
})
export class AppModule {
}
